# -*- coding: utf-8 -*-
"""
AgentScope学習用サンプル2：LLMとの連携

このスクリプトは、エージェントにOllama経由でローカルLLMを接続し、
対話させる方法を学びます。

【このサンプルで学べること】
- `OllamaChatModel` を使ってローカルLLMに接続する方法
- `ReActAgent` にモデルを組み込んで応答を生成させる方法
- `UserAgent` を使ってインタラクティブな対話を実現する方法
- AgentScope Studio (Webダッシュボード) との連携

【事前準備】
1. Ollamaがローカルマシンにインストールされ、実行中であること。
2. 対話に使用するモデルがOllamaにダウンロードされていること。
   (例: `ollama pull gpt-oss:20b`)
   このスクリプトでは 'gpt-oss:20b' をデフォルトとします。
3. AgentScope Studioを起動しておくこと。（任意）
   ターミナルで `as_studio` コマンドを実行すると、
   `http://localhost:3000` でダッシュボードが起動します。
"""

import asyncio
import agentscope
from agentscope.agent import ReActAgent, UserAgent
from agentscope.model import OllamaChatModel
from agentscope.formatter import OllamaChatFormatter
from agentscope.message import Msg

async def main():
    # --- 1. AgentScope Studioとの連携初期化 ---
    # `studio_url` を指定すると、対話の様子をWebダッシュボードで視覚的に確認できます。
    # このサンプルをすぐに実行できるように、デフォルトではこの行をコメントアウトしています。
    # AgentScope Studioを試す場合は、`as_studio`コマンドを実行し、
    # 以下の行のコメントを解除してください。
    print("AgentScopeを初期化しています...")
    agentscope.init(
        # studio_url="http://localhost:3000",
    )

    # --- 2. モデルの設定 ---
    # `OllamaChatModel`を使用して、ローカルで動作するOllamaのモデルを指定します。
    # `model_name` には、`ollama list` で表示されるモデル名を指定してください。
    # `formatter` は、モデルとの対話形式を整えるためのものです。
    # Ollamaを使う場合、`OllamaChatFormatter` を指定するのが一般的です。
    print("Ollamaモデルを設定しています...")
    # 'gpt-oss:20b' を使用します。
    # もし動作が重い場合は、'gemma:2b' など、より軽量なモデルに変更してください。
    llm_model = OllamaChatModel(
        model_name="gpt-oss:20b",
    )
    print(f"モデル '{llm_model.model_name}' の設定が完了しました。")


    # --- 3. エージェントの作成 ---
    # (1) アシスタントエージェント (ReActAgent)
    # `ReActAgent` は、思考(Reason)と行動(Act)を繰り返してタスクを解決するエージェントです。
    # LLMと連携させる場合に非常に強力です。
    # `sys_prompt` (システムプロンプト) で、エージェントの役割や性格を定義します。
    # `model` に、先ほど設定したLLMモデルのインスタンスを渡します。
    # `formatter` はモデルとのやり取りの形式を整えるために使います。
    print("アシスタントエージェントを作成しています...")
    assistant_agent = ReActAgent(
        name="アシスタント",
        sys_prompt="あなたは日本語で応答する、親切で優秀なアシスタントです。",
        model=llm_model,
        formatter=OllamaChatFormatter(),
    )

    # (2) ユーザーエージェント (UserAgent)
    # `UserAgent` は、コンソールからのユーザー入力を受け付けるための特別なエージェントです。
    print("ユーザーエージェントを作成しています...")
    user_agent = UserAgent(name="ユーザー")
    print("エージェントの作成が完了しました。\n")


    # --- 4. 対話ループの実行 ---
    print("--- 対話を開始します ---")
    print("対話を終了するには 'exit' と入力してください。")
    print("アシスタントへの最初の質問を入力してください。")

    msg = None
    while True:
        # `user_agent`を呼び出すと、コンソールからの入力を待ち受け、
        # その内容を`Msg`オブジェクトとして返します。
        # `user_agent`にメッセージを渡すと、その内容をコンソールに表示する機能もあります。
        # このループでは、アシスタントの応答(msg)をuser_agentに渡して表示し、
        # その後、新しいユーザーの入力を待つ、という動作を繰り返します。
        msg = await user_agent(msg)

        if msg.content == "exit":
            print("対話を終了します。")
            break

        # アシスタントエージェントが応答を生成するのを待つ
        assistant_response = await assistant_agent(msg)

        # アシスタントの応答を`msg`にセットして、次のループの最初に
        # `user_agent`によってコンソールに表示されるようにします。
        msg = assistant_response

# --- 5. 非同期関数の実行 ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムが中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
