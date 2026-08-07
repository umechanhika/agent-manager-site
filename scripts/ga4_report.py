#!/usr/bin/env python3
"""GA4 Data API から LP の日次 KPI データを取得し、整形 JSON を stdout に出力する。

KGI/KPI の定義は docs/kpi-tree.md を参照。数値の解釈・前日比・示唆の生成は
呼び出し側（日次レポート Routine の Claude）が行い、このスクリプトは取得と整形に徹する。
依存: python3 と openssl CLI のみ（RS256 署名に openssl を使用）。

必要な環境変数:
  GA4_SA_KEY_JSON  サービスアカウント鍵 JSON の全文（1行化した文字列。`jq -c . key.json` で生成）
  GA4_PROPERTY_ID  GA4 プロパティ ID（数値）

セットアップ手順は docs/setup-ga4-daily-report.md を参照。

検証用: `--print-request` を付けると、認証・ネットワークなしで
6 本の runReport リクエスト JSON のみを出力して終了する。
"""

import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
DATE_RANGE = {"startDate": "8daysAgo", "endDate": "yesterday"}


def report_requests():
    """runReport のリクエスト本体 6 本。date 付きで 8 日分取り、前日比・7日平均は後段で計算する。"""

    def event_filter(names):
        if len(names) == 1:
            return {"filter": {"fieldName": "eventName",
                               "stringFilter": {"value": names[0]}}}
        return {"filter": {"fieldName": "eventName",
                           "inListFilter": {"values": names}}}

    common = {"dateRanges": [DATE_RANGE], "orderBys": [{"dimension": {"dimensionName": "date"}}]}
    return {
        "daily": {
            **common,
            "dimensions": [{"name": "date"}],
            "metrics": [{"name": m} for m in (
                "sessions", "totalUsers", "newUsers", "engagementRate",
                "averageSessionDuration", "screenPageViews")],
        },
        "cta_click": {
            **common,
            "dimensions": [{"name": "date"}, {"name": "customEvent:cta_location"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": event_filter(["cta_click"]),
        },
        "section_view": {
            **common,
            "dimensions": [{"name": "date"}, {"name": "customEvent:section_id"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": event_filter(["section_view"]),
        },
        "channels": {
            **common,
            "dimensions": [{"name": "date"}, {"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "sessions"}],
        },
        "os": {
            **common,
            "dimensions": [{"name": "date"}, {"name": "operatingSystem"}],
            "metrics": [{"name": "sessions"}],
        },
        "other_events": {
            **common,
            "dimensions": [{"name": "date"}, {"name": "eventName"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": event_filter(
                ["producthunt_click", "faq_toggle", "hero_toggle", "scroll"]),
        },
    }


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign_rs256(private_key_pem: str, signing_input: bytes) -> bytes:
    """openssl CLI で RS256（RSA-PKCS#1v1.5 + SHA256）署名する。

    python 標準ライブラリに RSA 実装がなく、コンテナの cryptography パッケージは
    _cffi_backend 欠落で import 不能なため、openssl CLI を使う。
    鍵は所有者のみ読める一時ファイル（NamedTemporaryFile は 0600）経由で渡し、
    with を抜けた時点で削除される。
    """
    with tempfile.NamedTemporaryFile("w", suffix=".pem") as key_file:
        key_file.write(private_key_pem)
        key_file.flush()
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_file.name],
            input=signing_input, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"openssl 署名に失敗: {proc.stderr.decode(errors='replace')}")
    return proc.stdout


def fetch_access_token(sa_key: dict) -> str:
    now = int(time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64url(json.dumps({
        "iss": sa_key["client_email"],
        "scope": SCOPE,
        "aud": TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }).encode())
    signing_input = f"{header}.{claims}".encode("ascii")
    jwt = f"{header}.{claims}.{b64url(sign_rs256(sa_key['private_key'], signing_input))}"

    body = (
        "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer"
        f"&assertion={jwt}"
    ).encode("ascii")
    req = urllib.request.Request(
        TOKEN_URL, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def run_report(property_id: str, token: str, request_body: dict) -> list:
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    req = urllib.request.Request(
        url, data=json.dumps(request_body).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())

    dim_names = [h["name"] for h in data.get("dimensionHeaders", [])]
    met_names = [h["name"] for h in data.get("metricHeaders", [])]
    rows = []
    for row in data.get("rows", []):
        item = {}
        for name, v in zip(dim_names, row.get("dimensionValues", [])):
            item[name] = v["value"]
        for name, v in zip(met_names, row.get("metricValues", [])):
            item[name] = v["value"]
        rows.append(item)
    return rows


def main() -> None:
    requests_by_name = report_requests()

    if "--print-request" in sys.argv:
        print(json.dumps(requests_by_name, ensure_ascii=False, indent=2))
        return

    missing = [name for name in ("GA4_SA_KEY_JSON", "GA4_PROPERTY_ID")
               if not os.environ.get(name)]
    if missing:
        print(
            f"エラー: 環境変数 {', '.join(missing)} が未設定です。"
            "設定手順は docs/setup-ga4-daily-report.md を参照してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    sa_key = json.loads(os.environ["GA4_SA_KEY_JSON"])
    property_id = os.environ["GA4_PROPERTY_ID"]

    try:
        token = fetch_access_token(sa_key)
        reports = {name: run_report(property_id, token, body)
                   for name, body in requests_by_name.items()}
    except urllib.error.HTTPError as e:
        print(f"API エラー: HTTP {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)

    print(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "property": property_id,
        "date_range": DATE_RANGE,
        "reports": reports,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
