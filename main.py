# -*- coding: utf-8 -*-
"""
AgentScopeの主要な機能を学ぶためのテストプロジェクトです。

このスクリプトでは、以下の内容を実装しています。
- ローカルで動作するOllamaモデルとの連携
- ユーザーエージェントとアシスタントエージェントの2体による対話
- アシスタントエージェントへのツールの追加
- AgentScope Studio (Webダッシュボード) との連携
"""

import asyncio
import agentscope
from agentscope.agent import ReActAgent, UserAgent
from agentscope.model import OllamaChatModel
from agentscope.formatter import OllamaChatFormatter
from agentscope.tool import Toolkit
from agentscope.message import Msg
import datetime

# --- 1. AgentScope Studioとの連携初期化 ---
# AgentScopeの初期化を行います。
# `studio_url`で接続先のAgentScope Studioのアドレスを指定します。
# 事前に `as_studio` コマンドでWebダッシュボードを起動しておく必要があります。
# 今回はポート3000で起動しているため、そのように指定します。
print("AgentScope Studioへの接続を初期化しています...")
agentscope.init(
    studio_url="http://localhost:3000",
)
print("初期化が完了しました。")

# --- 2. ツールの定義 ---
# エージェントが使用できるツールを定義します。
# ツールとして使用する関数は、通常のPython関数として定義します。
def get_current_time() -> str:
    """
    現在の時刻を「YYYY-MM-DD HH:MM:SS」の形式で取得します。
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 3. モデルの設定 ---
# エージェントが使用するLLMモデルを設定します。
# ここでは、ローカルのOllamaで起動している 'gpt-oss:20b' モデルを使用します。
# `OllamaChatModel`クラスを使用し、`model_name`にモデル名を指定します。
# `max_tokens`はモデルが一度に生成するトークンの最大数です。
print("Ollamaモデルを設定しています...")
ollama_model = OllamaChatModel(
    model_name="gpt-oss:20b",
)
print("モデルの設定が完了しました。")


# --- 4. エージェントの作成 ---
# 対話に参加するエージェントを2体作成します。

# (1) アシスタントエージェント (ReActAgent)
# ReAct (Reasoning and Acting) の思考プロセスを持つエージェントです。
# まず、ツールを登録するためのToolkitオブジェクトを作成します。
toolkit = Toolkit()
toolkit.register_tool_function(get_current_time)

# `sys_prompt`でエージェントの役割や行動指針を日本語で設定します。
# `model`に先ほど設定したOllamaモデルを渡します。
# `toolkit`に作成したツールキットを渡します。
print("アシスタントエージェントを作成しています...")
assistant_agent = ReActAgent(
    name="アシスタント",
    sys_prompt="あなたは親切なアシスタントです。ユーザーの質問に答えたり、タスクを手伝ったりします。必要に応じて利用可能なツールを使ってください。",
    model=ollama_model,
    toolkit=toolkit,
    formatter=OllamaChatFormatter(),
)

# (2) ユーザーエージェント (UserAgent)
# ユーザーからの入力を受け取り、対話の起点となるエージェントです。
# デフォルトでコンソールからの入力を待ち受けます。
print("ユーザーエージェントを作成しています...")
user_agent = UserAgent(
    name="ユーザー",
)
print("エージェントの作成が完了しました。")

# --- 5. 対話の実行 ---
# 作成したエージェント間で対話を実行します。
# `async def` を使って非同期関数として定義するのが一般的です。
async def main() -> None:
    """
    メインの対話ループを実行します。
    """
    print("\n--- 対話を開始します ---")
    print("対話を終了するには 'exit' と入力してください。")
    print("最初の質問を入力してください。例: こんにちは、今の時間は？")

    # メッセージをNoneで初期化してループを開始
    msg = None

    while True:
        # ユーザーからの入力を待つ。初回呼び出しではmsgがNone
        msg = await user_agent(msg)

        # 'exit'が入力されたらループを抜ける
        if msg.content == "exit":
            print("対話を終了します。")
            break

        # アシスタントエージェントが応答を生成する
        msg = await assistant_agent(msg)

# Pythonの非同期イベントループを開始して、main関数を実行します。
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムが中断されました。")
