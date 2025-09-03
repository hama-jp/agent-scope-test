# AgentScopeプロジェクト開発における学び

このドキュメントは、AgentScopeのテストプロジェクト開発中に直面した技術的な問題とその解決策をまとめたものです。

## 1. 環境構築

### 依存関係の不足
- **問題:** `agentscope`のインストール後、実行時に`ModuleNotFoundError: No module named 'packaging'` や `No module named 'ollama'` が発生した。
- **解決策:** `agentscope`の必須ライブラリが`setup.py`に完全には含まれていないようだった。以下のコマンドで、不足しているライブラリを手動でインストールした。
  ```bash
  pip install packaging
  pip install "ollama>=0.1.7"
  ```

### AgentScope Studioのインストール
- **問題:** `npm install -g agentscope-studio` が404エラーで失敗した。
- **解決策:** 公式のGitHubリポジトリを確認したところ、正しいパッケージ名は `@agentscope/studio` であった。以下のコマンドで正しくインストールできた。
  ```bash
  npm install -g @agentscope/studio
  ```

## 2. AgentScope APIの利用

AgentScopeのドキュメントと実際のAPIの挙動にいくつか差異が見られた。

- **`agentscope.init()` 関数:**
  - **問題:** `project_name`や`save_dir`といった引数を渡すと `TypeError` が発生した。
  - **解決策:** ドキュメントの最小限の例に従い、Studioとの連携には `studio_url` のみを引数として渡すことで解決した。

- **モデルクラスの指定:**
  - **問題:** `OllamaChat` というクラス名でインポートしようとして `ImportError` が発生した。また、`max_tokens`引数で `TypeError` が発生した。
  - **解決策:** パッケージ内部を確認し、正しいクラス名は `OllamaChatModel` であることを特定した。また、`max_tokens` はコンストラクタでサポートされていない引数だったため削除した。

- **ツールの定義と登録:**
  - **問題:** `@tool_fn` デコレータが存在せず `ImportError` となった。
  - **解決策:** `Toolkit` オブジェクトを使用するのが正しい方法だった。`Toolkit`をインスタンス化し、`register_tool_function()` メソッドで関数を登録し、その`toolkit`オブジェクトをエージェントに渡した。

- **`ReActAgent`の初期化:**
  - **問題:** `formatter` 引数が必須であるにもかかわらず渡していなかったため `TypeError` が発生した。
  - **解決策:** Ollamaモデルに対応する `OllamaChatFormatter` をインポートし、インスタンス化して引数に渡した。

- **`UserAgent`の初期化:**
  - **問題:** `require_human_input=True` という引数がサポートされておらず `TypeError` が発生した。
  - **解決策:** 引数を削除した。`UserAgent`はデフォルトでコンソールからの入力を受け付ける仕様だった。

- **`Msg`オブジェクトの作成:**
  - **問題:** `Msg()` の初期化時に `role` 引数が必須だったため `TypeError` が発生した。
  - **解決策:** 対話ループの開始前に `msg = None` と初期化するのが正しいパターンだった。`UserAgent`が最初の入力から適切な`role`を持つ`Msg`オブジェクトを生成するため。

- **エージェントの呼び出し:**
  - **問題:** `agent.call(msg)` というメソッド呼び出しで `AttributeError` が発生した。
  - **解決策:** AgentScopeのエージェントは直接呼び出し可能オブジェクトだった。`agent(msg)` のように呼び出すことで解決した。
