# -*- coding: utf-8 -*-
"""
AgentScope学習用サンプル4：複数エージェントの協調

このスクリプトは、複数のエージェントがそれぞれ異なる役割を持ち、
協調して一つのタスクを解決する、より高度な対話フローを学びます。

ここでは、「プランナー（計画者）」と「クリティック（批評家）」という
2体のLLM搭載エージェントを作成し、ユーザーの要望に応じた計画を
協力して作り上げる様子を実装します。

【このサンプルで学べること】
- 複数のLLMエージェントに異なる役割（プロンプト）を与えて設定する方法
- 特定の順序でエージェントを呼び出し、対話フローを制御する方法
- エージェント間の協調によって、より質の高い応答を生成する考え方

【事前準備】
- `sample2_with_llm.py`と同様のOllama環境。

【実行時のヒント】
- 起動後、「Pythonを学ぶための計画を立てて」や「3日間の旅行プランを考えて」など、
  計画を立ててほしいタスクを入力してみてください。
"""

import asyncio
import agentscope
from agentscope.agent import ReActAgent, UserAgent
from agentscope.model import OllamaChatModel
from agentscope.formatter import OllamaChatFormatter
from agentscope.message import Msg

async def main():
    # AgentScopeの初期化
    print("AgentScopeを初期化しています...")
    agentscope.init()

    # --- 1. モデルの設定 ---
    # 全てのエージェントで共有するモデルを1つ定義します。
    print("Ollamaモデルを設定しています...")
    llm_model = OllamaChatModel(model_name="gemma:2b")
    print(f"モデル '{llm_model.model_name}' の設定が完了しました。")

    # --- 2. エージェントの作成 ---
    # (1) プランナーエージェント
    # タスクを受け取り、ステップバイステップの計画を生成する役割。
    print("プランナーエージェントを作成しています...")
    planner_agent = ReActAgent(
        name="プランナー",
        sys_prompt="あなたは優秀な計画立案者です。ユーザーから与えられたタスクに対して、具体的で実行可能なステップバイステップの計画を作成してください。",
        model=llm_model,
        formatter=OllamaChatFormatter(),
    )

    # (2) クリティックエージェント
    # プランナーが作った計画をレビューし、改善点を提案する役割。
    print("クリティックエージェントを作成しています...")
    critic_agent = ReActAgent(
        name="クリティック",
        sys_prompt="あなたは優秀な批評家です。与えられた計画を注意深くレビューし、その計画の潜在的な問題点、欠けている視点、改善のための具体的な提案を指摘してください。",
        model=llm_model,
        formatter=OllamaChatFormatter(),
    )

    # (3) ユーザーエージェント
    print("ユーザーエージェントを作成しています...")
    user_agent = UserAgent(name="ユーザー")
    print("エージェントの作成が完了しました。\n")


    # --- 3. 対話フローの実行 ---
    print("--- 複数エージェントによる協調タスクを開始します ---")
    print("計画したいタスクを入力してください。例：Pythonを学ぶための計画を立てて")
    print("終了するには 'exit' と入力してください。")

    while True:
        # (Step 1) ユーザーからタスクを受け取る
        # UserAgentを引数なしで呼び出すと、ユーザーからの新規入力を待ち受け、
        # `Msg`オブジェクトとして返します。
        user_msg = await user_agent()
        if user_msg.content == "exit":
            print("対話を終了します。")
            break
        print(f"\n--- [ユーザー]さんのリクエスト: ---\n{user_msg.content}\n" + "-"*20)

        # (Step 2) プランナーが計画を立案
        print("\n--- [プランナー]が計画を立案中... ---")
        plan_msg = await planner_agent(user_msg)
        print(f"\n--- [プランナー]からの計画案: ---\n{plan_msg.content}\n" + "-"*20)

        # (Step 3) クリティックが計画をレビュー
        print("\n--- [クリティック]が計画をレビュー中... ---")
        # クリティックには、元のタスクと計画案の両方を渡すことで、より的確な批判が可能になります。
        # ここでは簡単のため、計画案だけを渡します。
        critique_msg = await critic_agent(plan_msg)
        print(f"\n--- [クリティック]からの改善案: ---\n{critique_msg.content}\n" + "-"*20)

        # (Step 4) 最終結果をユーザーに提示
        # 実際には、この後さらにプランナーに修正させたりできますが、
        # このサンプルではクリティックの意見を最終結果として表示します。
        print("\n★★★ 最終的な提案 ★★★")
        print("【計画案】\n" + plan_msg.content)
        print("\n【改善案】\n" + critique_msg.content)
        print("★★★★★★★★★★★★★★★★\n")
        print("次のタスクを入力してください。('exit'で終了)")


# --- 4. 非同期関数の実行 ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムが中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
