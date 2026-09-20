/*
 * Claude Code hooks builder — event catalog and settings generator.
 *
 * Pure logic, no DOM. The page (claude-code-hooks-builder.html) renders the
 * form from HOOK_EVENTS and calls buildSettings(); Tests/test_hooks_builder.py
 * runs the same file under node and checks the output against the documented
 * settings.json schema.
 *
 * Event list and matcher values follow the official docs
 * (https://code.claude.com/docs/en/hooks), checked 2026-09-20.
 *
 * buildSettings() throws on invalid input instead of guessing a default —
 * the page shows the message in place of the output.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.HooksBuilder = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // group: section heading in the form.
  // matcher: null = not supported; otherwise a short label of what it matches.
  // hint: example matcher values (shown as placeholder).
  var HOOK_EVENTS = [
    // ── Session lifecycle ────────────────────────────────────────────
    { name: 'SessionStart', group: 'session',
      desc: { en: 'A session starts or resumes', ja: 'セッションが開始・再開した' },
      matcher: { en: 'how it started', ja: '開始の種類' }, hint: 'startup|resume|clear|compact|fork' },
    { name: 'Setup', group: 'session',
      desc: { en: 'Runs for --init / --maintenance setup', ja: '--init / --maintenance のセットアップ時' },
      matcher: { en: 'setup trigger', ja: 'セットアップの種類' }, hint: 'init|maintenance' },
    { name: 'UserPromptSubmit', group: 'session',
      desc: { en: 'You submit a prompt, before Claude reads it', ja: 'プロンプトを送信した（Claude が読む前）' },
      matcher: null },
    { name: 'UserPromptExpansion', group: 'session',
      desc: { en: 'A slash command expands into a prompt', ja: 'スラッシュコマンドがプロンプトに展開された' },
      matcher: null },
    { name: 'Stop', group: 'session',
      desc: { en: 'The main agent finishes its response', ja: 'メインエージェントの応答が終わった' },
      matcher: null },
    { name: 'StopFailure', group: 'session',
      desc: { en: 'The turn ends because of an API error', ja: 'API エラーでターンが止まった' },
      matcher: { en: 'error type', ja: 'エラーの種類' },
      hint: 'rate_limit|overloaded|authentication_failed|billing_error|max_output_tokens|unknown' },
    { name: 'Notification', group: 'session',
      desc: { en: 'Claude Code needs your attention (permission prompt, idle…)', ja: '確認が必要になった（許可待ち・放置…）' },
      matcher: { en: 'notification type', ja: '通知の種類' },
      hint: 'permission_prompt|idle_prompt|elicitation_dialog|agent_needs_input' },
    { name: 'SessionEnd', group: 'session',
      desc: { en: 'The session terminates', ja: 'セッションが終了した' },
      matcher: { en: 'why it ended', ja: '終了理由' }, hint: 'clear|resume|logout|prompt_input_exit|other' },

    // ── Tools and permissions ────────────────────────────────────────
    { name: 'PreToolUse', group: 'tools',
      desc: { en: 'Before a tool call runs (can block it)', ja: 'ツール実行の直前（ブロック可能）' },
      matcher: { en: 'tool name', ja: 'ツール名' }, hint: 'Bash|Edit|Write|mcp__.*' },
    { name: 'PermissionRequest', group: 'tools',
      desc: { en: 'A tool call needs a permission decision', ja: 'ツール実行に許可の判断が必要になった' },
      matcher: { en: 'tool name', ja: 'ツール名' }, hint: 'Bash|Edit|Write' },
    { name: 'PermissionDenied', group: 'tools',
      desc: { en: 'Auto mode denied a tool call', ja: '自動モードがツール実行を拒否した' },
      matcher: { en: 'tool name', ja: 'ツール名' }, hint: 'Bash|Edit|Write' },
    { name: 'PostToolUse', group: 'tools',
      desc: { en: 'After a tool call succeeds', ja: 'ツール実行が成功した後' },
      matcher: { en: 'tool name', ja: 'ツール名' }, hint: 'Bash|Edit|Write|mcp__.*' },
    { name: 'PostToolUseFailure', group: 'tools',
      desc: { en: 'After a tool call fails', ja: 'ツール実行が失敗した後' },
      matcher: { en: 'tool name', ja: 'ツール名' }, hint: 'Bash|Edit|Write' },
    { name: 'PostToolBatch', group: 'tools',
      desc: { en: 'A batch of parallel tool calls has all resolved', ja: '並列ツール呼び出しの一括分がすべて終わった' },
      matcher: null },
    { name: 'MessageDisplay', group: 'tools',
      desc: { en: 'An assistant message is displayed', ja: 'アシスタントのメッセージが表示された' },
      matcher: null },

    // ── Subagents and tasks ──────────────────────────────────────────
    { name: 'SubagentStart', group: 'agents',
      desc: { en: 'A subagent is spawned', ja: 'サブエージェントが起動した' },
      matcher: { en: 'agent type', ja: 'エージェント種別' }, hint: 'general-purpose|Explore|Plan' },
    { name: 'SubagentStop', group: 'agents',
      desc: { en: 'A subagent finishes', ja: 'サブエージェントが終了した' },
      matcher: { en: 'agent type', ja: 'エージェント種別' }, hint: 'general-purpose|Explore|Plan' },
    { name: 'TaskCreated', group: 'agents',
      desc: { en: 'A task is created', ja: 'タスクが作成された' },
      matcher: null },
    { name: 'TaskCompleted', group: 'agents',
      desc: { en: 'A task is marked completed', ja: 'タスクが完了になった' },
      matcher: null },
    { name: 'TeammateIdle', group: 'agents',
      desc: { en: 'An agent-team teammate is about to go idle', ja: 'エージェントチームのメンバーが待機に入る直前' },
      matcher: null },

    // ── Context, config, model ───────────────────────────────────────
    { name: 'PreCompact', group: 'context',
      desc: { en: 'Before the context is compacted', ja: 'コンテキスト圧縮の直前' },
      matcher: { en: 'trigger', ja: 'トリガー' }, hint: 'manual|auto' },
    { name: 'PostCompact', group: 'context',
      desc: { en: 'After compaction completes', ja: 'コンテキスト圧縮の完了後' },
      matcher: { en: 'trigger', ja: 'トリガー' }, hint: 'manual|auto' },
    { name: 'InstructionsLoaded', group: 'context',
      desc: { en: 'A CLAUDE.md or rules file is loaded', ja: 'CLAUDE.md やルールファイルが読み込まれた' },
      matcher: { en: 'load reason', ja: '読み込み理由' }, hint: 'session_start|nested_traversal|path_glob_match|include|compact' },
    { name: 'ConfigChange', group: 'context',
      desc: { en: 'A settings file changes during the session', ja: 'セッション中に設定ファイルが変わった' },
      matcher: { en: 'config source', ja: '設定の種類' }, hint: 'user_settings|project_settings|local_settings|policy_settings|skills' },
    { name: 'PreModelSwitch', group: 'context',
      desc: { en: 'Before a model switch (can block it)', ja: 'モデル切り替えの直前（ブロック可能）' },
      matcher: { en: 'target model', ja: '切り替え先モデル' }, hint: '.*opus.*' },
    { name: 'PostModelSwitch', group: 'context',
      desc: { en: 'After the session model changes', ja: 'モデルが切り替わった後' },
      matcher: { en: 'target model', ja: '切り替え先モデル' }, hint: '.*opus.*' },
    { name: 'Elicitation', group: 'context',
      desc: { en: 'An MCP server asks you for input', ja: 'MCP サーバーが入力を求めた' },
      matcher: { en: 'MCP server name', ja: 'MCP サーバー名' }, hint: 'my-server' },
    { name: 'ElicitationResult', group: 'context',
      desc: { en: 'You answered an MCP elicitation', ja: 'MCP サーバーの入力要求に応答した' },
      matcher: { en: 'MCP server name', ja: 'MCP サーバー名' }, hint: 'my-server' },

    // ── Workspace ────────────────────────────────────────────────────
    { name: 'CwdChanged', group: 'workspace',
      desc: { en: 'The working directory changes', ja: '作業ディレクトリが変わった' },
      matcher: null },
    { name: 'DirectoryAdded', group: 'workspace',
      desc: { en: 'A directory is added with /add-dir', ja: '/add-dir でディレクトリが追加された' },
      matcher: { en: 'how it was added', ja: '追加方法' }, hint: 'slash_command|register_repo_root' },
    { name: 'FileChanged', group: 'workspace',
      desc: { en: 'A watched file changes on disk', ja: '監視中のファイルが変更された' },
      matcher: { en: 'file names (literal, | separated)', ja: 'ファイル名（正規表現ではなく | 区切り）' }, hint: '.envrc|.env' },
    { name: 'WorktreeCreate', group: 'workspace',
      desc: { en: 'A git worktree is being created', ja: 'git worktree が作成される' },
      matcher: null },
    { name: 'WorktreeRemove', group: 'workspace',
      desc: { en: 'A git worktree is being removed', ja: 'git worktree が削除される' },
      matcher: null }
  ];

  var GROUPS = [
    { id: 'session',   label: { en: 'Session lifecycle',        ja: 'セッションのライフサイクル' } },
    { id: 'tools',     label: { en: 'Tools and permissions',    ja: 'ツールと許可' } },
    { id: 'agents',    label: { en: 'Subagents and tasks',      ja: 'サブエージェントとタスク' } },
    { id: 'context',   label: { en: 'Context, config, model',   ja: 'コンテキスト・設定・モデル' } },
    { id: 'workspace', label: { en: 'Workspace',                ja: 'ワークスペース' } }
  ];

  // Presets fill the form; they are plain specs for buildSettings().
  var PRESETS = [
    { id: 'notify',
      label: { en: 'Notify me when Claude needs me (macOS)', ja: '確認が必要になったら通知する（macOS）' },
      spec: {
        events: [{ name: 'Stop' }, { name: 'Notification' }],
        command: "osascript -e 'display notification \"Check your terminal\" with title \"Claude Code\"'"
      } },
    { id: 'status',
      label: { en: 'Track session status (waiting / running / done)', ja: 'セッション状態を追跡する（確認待ち / 処理中 / 完了）' },
      spec: {
        events: [
          { name: 'SessionStart' }, { name: 'UserPromptSubmit' }, { name: 'PreToolUse' },
          { name: 'PostToolUse' }, { name: 'Notification' }, { name: 'Stop' }, { name: 'StopFailure' },
          { name: 'SubagentStart' }, { name: 'SubagentStop' }, { name: 'SessionEnd' }, { name: 'PreCompact' }
        ],
        command: '$HOME/.claude/hooks/session-status.sh',
        statusLine: { command: '$HOME/.claude/hooks/session-status.sh statusline' }
      } },
    { id: 'log',
      label: { en: 'Log every tool call to a file', ja: 'ツール呼び出しをすべてファイルに記録する' },
      spec: {
        events: [{ name: 'PreToolUse' }, { name: 'PostToolUse' }],
        command: 'jq -c . >> "$HOME/.claude/tool-calls.jsonl"'
      } },
    { id: 'guard',
      label: { en: 'Block destructive shell commands', ja: '破壊的なシェルコマンドをブロックする' },
      spec: {
        events: [{ name: 'PreToolUse', matcher: 'Bash' }],
        command: '$HOME/.claude/hooks/guard-bash.sh',
        timeout: 10
      } }
  ];

  var TARGETS = [
    { id: 'user',    path: '~/.claude/settings.json',
      label: { en: 'User — every project on this machine', ja: 'ユーザー — この Mac の全プロジェクト' } },
    { id: 'project', path: '.claude/settings.json',
      label: { en: 'Project — committed, shared with the team', ja: 'プロジェクト — コミットしてチームと共有' } },
    { id: 'local',   path: '.claude/settings.local.json',
      label: { en: 'Project local — not committed', ja: 'プロジェクト（ローカル）— コミットしない' } }
  ];

  var byName = {};
  HOOK_EVENTS.forEach(function (e) { byName[e.name] = e; });

  function fail(msg) { throw new Error(msg); }

  function nonEmpty(value, what) {
    if (typeof value !== 'string' || value.trim() === '') fail(what + ' is required');
    return value.trim();
  }

  /**
   * spec = {
   *   events: [{ name: 'PreToolUse', matcher?: 'Bash' }, ...]   // at least one
   *   command: '...'                                             // required
   *   timeout?: positive integer (seconds)
   *   statusLine?: { command: '...' }
   * }
   * Returns the settings object ({ hooks: {...}, statusLine?: {...} }).
   */
  function buildSettings(spec) {
    if (!spec || typeof spec !== 'object') fail('spec must be an object');
    if (!Array.isArray(spec.events) || spec.events.length === 0) fail('select at least one event');

    var command = nonEmpty(spec.command, 'command');

    var timeout;
    if (spec.timeout !== undefined && spec.timeout !== null && spec.timeout !== '') {
      timeout = Number(spec.timeout);
      if (!Number.isInteger(timeout) || timeout <= 0) fail('timeout must be a positive whole number of seconds');
    }

    var hooks = {};
    var seen = {};
    spec.events.forEach(function (ev) {
      if (!ev || typeof ev.name !== 'string') fail('event entry must have a name');
      var def = byName[ev.name];
      if (!def) fail('unknown hook event: ' + ev.name);
      if (seen[ev.name]) fail('event listed twice: ' + ev.name);
      seen[ev.name] = true;

      var matcher = (typeof ev.matcher === 'string') ? ev.matcher.trim() : '';
      if (matcher !== '' && !def.matcher) fail(ev.name + ' does not support a matcher');

      var handler = { type: 'command', command: command };
      if (timeout !== undefined) handler.timeout = timeout;

      var entry = {};
      if (matcher !== '') entry.matcher = matcher;
      entry.hooks = [handler];
      hooks[ev.name] = [entry];
    });

    var settings = { hooks: hooks };

    if (spec.statusLine !== undefined && spec.statusLine !== null) {
      if (typeof spec.statusLine !== 'object') fail('statusLine must be an object');
      settings.statusLine = { type: 'command', command: nonEmpty(spec.statusLine.command, 'statusLine command') };
    }

    return settings;
  }

  function toJSON(settings) {
    return JSON.stringify(settings, null, 2) + '\n';
  }

  return {
    HOOK_EVENTS: HOOK_EVENTS,
    GROUPS: GROUPS,
    PRESETS: PRESETS,
    TARGETS: TARGETS,
    buildSettings: buildSettings,
    toJSON: toJSON
  };
}));
