#!/usr/bin/env python3
"""hooks ビルダー（tools/hooks-builder.js）の生成結果が Claude Code の settings.json スキーマに
沿っていることを検査する。

    python3 Tests/test_hooks_builder.py

ビルダーは公開ツールで「そのまま貼れる有効な設定」を売りにしている。生成ロジックは
ブラウザと同じファイルを node で実行して検査する（DOM に依存しない純粋関数のため）。
スキーマは公式ドキュメント（https://code.claude.com/docs/en/hooks）の
  {"hooks": {"<Event>": [{"matcher"?: str, "hooks": [{"type": "command", "command": str, "timeout"?: int}]}]}}
と statusLine の {"type": "command", "command": str} を正とする。

検査する不変条件:

1. 全プリセットが例外なく生成でき、上の形に一致する（未知のキー・型違いが無い）
2. matcher は対応イベントにだけ付き、非対応イベントに指定すると例外になる
3. 空コマンド・イベント未選択・不正な timeout は既定値で埋めずに例外になる（フォールバック禁止）
4. カタログのイベント名に重複が無く、参照ページの一覧と一致する
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "tools" / "hooks-builder.js"
REFERENCE = ROOT / "guides" / "claude-code-hooks-reference.html"

NODE = shutil.which("node")

HARNESS = r"""
const HB = require(process.argv[1]);
const cases = JSON.parse(process.argv[2]);
const out = {};
for (const [key, spec] of Object.entries(cases)) {
  try { out[key] = { ok: HB.buildSettings(spec) }; }
  catch (e) { out[key] = { error: e.message, code: e.code }; }
}
out.__catalog = HB.HOOK_EVENTS.map(e => ({ name: e.name, matcher: !!e.matcher, group: e.group }));
out.__presets = HB.PRESETS.map(p => p.id);
out.__groups = HB.GROUPS.map(g => g.id);
out.__preset_specs = Object.fromEntries(HB.PRESETS.map(p => [p.id, p.spec]));
process.stdout.write(JSON.stringify(out));
"""


def run_builder(cases):
    """node で buildSettings() を呼び、結果（ok または error）とカタログを返す。"""
    proc = subprocess.run(
        [NODE, "-e", HARNESS, str(BUILDER), json.dumps(cases)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)


def assert_valid_settings(test, settings, catalog):
    known = {e["name"]: e for e in catalog}
    test.assertLessEqual(set(settings), {"hooks", "statusLine"})
    test.assertIn("hooks", settings)
    test.assertGreater(len(settings["hooks"]), 0)
    for event, entries in settings["hooks"].items():
        test.assertIn(event, known, f"unknown event in output: {event}")
        test.assertIsInstance(entries, list)
        for entry in entries:
            test.assertLessEqual(set(entry), {"matcher", "hooks"})
            if "matcher" in entry:
                test.assertTrue(known[event]["matcher"], f"{event} has a matcher but does not support one")
                test.assertIsInstance(entry["matcher"], str)
                test.assertNotEqual(entry["matcher"], "")
            test.assertIsInstance(entry["hooks"], list)
            test.assertGreater(len(entry["hooks"]), 0)
            for handler in entry["hooks"]:
                test.assertLessEqual(set(handler), {"type", "command", "timeout"})
                test.assertEqual(handler["type"], "command")
                test.assertIsInstance(handler["command"], str)
                test.assertNotEqual(handler["command"].strip(), "")
                if "timeout" in handler:
                    test.assertIsInstance(handler["timeout"], int)
                    test.assertGreater(handler["timeout"], 0)
    if "statusLine" in settings:
        test.assertEqual(set(settings["statusLine"]), {"type", "command"})
        test.assertEqual(settings["statusLine"]["type"], "command")
        test.assertNotEqual(settings["statusLine"]["command"].strip(), "")


@unittest.skipIf(NODE is None, "node が無い環境では実行できない")
class TestBuildSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_builder({
            "minimal": {"events": [{"name": "Stop"}], "command": "echo hi"},
            "matcher": {"events": [{"name": "PreToolUse", "matcher": "Bash|Edit"}], "command": "x", "timeout": 10},
            "matcher_blank_dropped": {"events": [{"name": "PreToolUse", "matcher": "   "}], "command": "x"},
            "timeout_string": {"events": [{"name": "Stop"}], "command": "x", "timeout": "30"},
            "statusline": {"events": [{"name": "Stop"}], "command": "x", "statusLine": {"command": "y"}},
            # 例外になるべき入力
            "no_events": {"events": [], "command": "x"},
            "empty_command": {"events": [{"name": "Stop"}], "command": "   "},
            "unknown_event": {"events": [{"name": "Nope"}], "command": "x"},
            "duplicate_event": {"events": [{"name": "Stop"}, {"name": "Stop"}], "command": "x"},
            "matcher_unsupported": {"events": [{"name": "Stop", "matcher": "x"}], "command": "x"},
            "timeout_zero": {"events": [{"name": "Stop"}], "command": "x", "timeout": 0},
            "timeout_float": {"events": [{"name": "Stop"}], "command": "x", "timeout": 1.5},
            "statusline_empty": {"events": [{"name": "Stop"}], "command": "x", "statusLine": {"command": ""}},
        })
        cls.catalog = cls.result["__catalog"]

    def ok(self, key):
        self.assertIn("ok", self.result[key], self.result[key].get("error"))
        return self.result[key]["ok"]

    def error(self, key):
        self.assertIn("error", self.result[key], f"{key} should have raised")
        return self.result[key]["error"]

    def test_minimal_shape(self):
        settings = self.ok("minimal")
        assert_valid_settings(self, settings, self.catalog)
        self.assertEqual(settings, {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}})

    def test_matcher_and_timeout(self):
        settings = self.ok("matcher")
        assert_valid_settings(self, settings, self.catalog)
        entry = settings["hooks"]["PreToolUse"][0]
        self.assertEqual(entry["matcher"], "Bash|Edit")
        self.assertEqual(entry["hooks"][0]["timeout"], 10)

    def test_blank_matcher_is_omitted_not_emitted_empty(self):
        entry = self.ok("matcher_blank_dropped")["hooks"]["PreToolUse"][0]
        self.assertNotIn("matcher", entry)

    def test_timeout_from_form_string_becomes_integer(self):
        self.assertEqual(self.ok("timeout_string")["hooks"]["Stop"][0]["hooks"][0]["timeout"], 30)

    def test_statusline(self):
        settings = self.ok("statusline")
        assert_valid_settings(self, settings, self.catalog)
        self.assertEqual(settings["statusLine"], {"type": "command", "command": "y"})

    def test_invalid_inputs_raise_instead_of_defaulting(self):
        self.assertIn("at least one event", self.error("no_events"))
        self.assertIn("command", self.error("empty_command"))
        self.assertIn("unknown hook event", self.error("unknown_event"))
        self.assertIn("twice", self.error("duplicate_event"))
        self.assertIn("does not support a matcher", self.error("matcher_unsupported"))
        self.assertIn("timeout", self.error("timeout_zero"))
        self.assertIn("timeout", self.error("timeout_float"))
        self.assertIn("statusLine command", self.error("statusline_empty"))

    def test_user_reachable_errors_carry_localisable_codes(self):
        # UI 側（hooks-builder-ui.js）が err.code で翻訳を引くため、利用者が到達しうる 4 種にだけコードを付ける。
        self.error("no_events")
        self.assertEqual(self.result["no_events"]["code"], "no_events")
        self.error("empty_command")
        self.assertEqual(self.result["empty_command"]["code"], "command_required")
        self.error("statusline_empty")
        self.assertEqual(self.result["statusline_empty"]["code"], "statusline_command_required")
        self.error("timeout_zero")
        self.assertEqual(self.result["timeout_zero"]["code"], "timeout_invalid")
        self.error("timeout_float")
        self.assertEqual(self.result["timeout_float"]["code"], "timeout_invalid")
        # プログラミングエラー（不正なイベント名）にはコードを付けない（JSON.stringify で undefined は落ちる）。
        self.error("unknown_event")
        self.assertNotIn("code", self.result["unknown_event"])


@unittest.skipIf(NODE is None, "node が無い環境では実行できない")
class TestPresetsAndCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = run_builder({})
        cls.catalog = probe["__catalog"]
        cls.groups = probe["__groups"]
        cls.preset_ids = probe["__presets"]
        cls.presets = run_builder(probe["__preset_specs"])

    def test_every_preset_builds_valid_settings(self):
        self.assertGreater(len(self.preset_ids), 0)
        for pid in self.preset_ids:
            self.assertIn("ok", self.presets[pid], f"preset {pid}: {self.presets[pid].get('error')}")
            assert_valid_settings(self, self.presets[pid]["ok"], self.catalog)

    def test_catalog_names_are_unique_and_grouped(self):
        names = [e["name"] for e in self.catalog]
        self.assertEqual(len(names), len(set(names)), "duplicate event names in catalog")
        for e in self.catalog:
            self.assertIn(e["group"], self.groups, f"{e['name']} has unknown group {e['group']}")

    def test_catalog_matches_reference_page(self):
        """参照ページ（引用される一覧）とビルダーのイベント一覧が食い違わないことを固定する。"""
        if not REFERENCE.exists():
            self.skipTest("参照ページ未作成")
        html = REFERENCE.read_text(encoding="utf-8")
        table = re.search(r'<table[^>]*id="hook-events"[^>]*>(.*?)</table>', html, re.S)
        self.assertIsNotNone(table, "参照ページに id=\"hook-events\" の表が無い")
        in_page = re.findall(r"<tr>\s*<td><code>([A-Za-z]+)</code>", table.group(1))
        self.assertEqual(sorted(in_page), sorted(e["name"] for e in self.catalog))


if __name__ == "__main__":
    unittest.main(verbosity=2)
