# -*- coding: utf-8 -*-
"""
AgentScope学習用サンプル3：ツールの利用

このスクリプトは、エージェントにカスタムツール（関数）を渡し、
LLMの判断でそのツールを使わせる方法を学びます。

【このサンプルで学べること】
- Python関数をエージェントのツールとして定義する方法
- `Toolkit`を使ってツールを管理する方法
- `ReActAgent`にツールキットを渡し、自律的にツールを使わせる方法

【事前準備】
- `sample2_with_llm.py`と同様のOllama環境。

【実行時のヒント】
- 起動後、「今の時間は？」や「現在時刻を教えて」と入力してみてください。
- エージェントが`get_current_time`ツールを呼び出し、その結果を元に応答を生成する様子が確認できます。
"""

import asyncio
import datetime
import agentscope
from agentscope.agent import ReActAgent, UserAgent
from agentscope.model import OllamaChatModel
from agentscope.formatter import OllamaChatFormatter
from agentscope.tool import Toolkit
from agentscope.message import Msg

# --- 1. ツールの定義 ---
# エージェントが使用できるツールを、通常のPython関数として定義します。
# ★重要★
# 関数のdocstring（三重クォートで囲まれた説明文）は非常に重要です。
# LLMはこのdocstringを読んで、いつ、どのようにこのツールを使うべきかを判断します。
# そのため、引数や返り値について分かりやすく記述する必要があります。
def get_current_time() -> str:
    """
    現在の時刻を「YYYY-MM-DD HH:MM:SS」の形式で取得します。
    この関数は引数を必要としません。
    """
    print("\n--- [ツール実行] get_current_timeが呼び出されました ---")
    result = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- [ツール実行] 結果: {result} ---\n")
    return result

async def main():
    # AgentScopeの初期化 (Studio連携はコメントアウト)
    print("AgentScopeを初期化しています...")
    agentscope.init()

    # --- 2. モデルの設定 ---
    print("Ollamaモデルを設定しています...")
    llm_model = OllamaChatModel(
        model_name="gemma:2b",
    )
    print(f"モデル '{llm_model.model_name}' の設定が完了しました。")

    # --- 3. ツールキットの作成 ---
    # `Toolkit`オブジェクトを作成し、定義した関数をツールとして登録します。
    print("ツールキットを作成し、ツールを登録しています...")
    toolkit = Toolkit()
    toolkit.register_tool_function(get_current_time)
    print("ツールの登録が完了しました。")

    # --- 4. エージェントの作成 ---
    # (1) アシスタントエージェント (ReActAgent)
    # `sys_prompt`を更新し、ツールを積極的に使うように指示します。
    # `toolkit`引数に、作成したツールキットのインスタンスを渡します。
    print("アシスタントエージェントを作成しています...")
    assistant_agent = ReActAgent(
        name="アシスタント",
        sys_prompt="あなたは日本語で応答する、親切で優秀なアシスタントです。必要に応じて、利用可能なツールを積極的に使ってユーザーの質問に答えてください。",
        model=llm_model,
        formatter=OllamaChatFormatter(),
        toolkit=toolkit, # ★ここにツールキットを渡す
    )

    # (2) ユーザーエージェント (UserAgent)
    print("ユーザーエージェントを作成しています...")
    user_agent = UserAgent(name="ユーザー")
    print("エージェントの作成が完了しました。\n")


    # --- 5. 対話ループの実行 ---
    print("--- 対話を開始します ---")
    print("対話を終了するには 'exit' と入力してください。")
    print("アシスタントへの最初の質問を入力してください。例：今の時間は？")

    msg = None
    while True:
        msg = await user_agent(msg)

        if msg.content == "exit":
            print("対話を終了します。")
            break

        assistant_response = await assistant_agent(msg)
        msg = assistant_response

# --- 6. 非同期関数の実行 ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムが中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
