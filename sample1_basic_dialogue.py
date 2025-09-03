# -*- coding: utf-8 -*-
"""
AgentScope学習用サンプル1：エージェント間の基本対話

このスクリプトは、AgentScopeの最も基本的な機能である、
エージェント間のメッセージ交換を学ぶためのものです。
LLMや複雑なツールは使用せず、2体のエージェントが
どのように対話し、メッセージをやり取りするかに焦点を当てます。

【このサンプルで学べること】
- `AgentBase`を継承したカスタムエージェントの作り方
- `Msg`オブジェクトを使ったメッセージの表現方法
- エージェント間で同期的にメッセージを交換する方法
"""

import asyncio
import agentscope
from agentscope.agent import AgentBase
from agentscope.message import Msg

# --- 1. AgentScopeの初期化 ---
# AgentScopeを使用する前には、`init()`を呼び出す必要があります。
# 今回はWebダッシュボード(Studio)やモデルは使わないため、引数は不要です。
agentscope.init()

# --- 2. カスタムエージェントの定義 ---
# AgentScopeのすべてのエージェントの基本となる`AgentBase`を継承して、
# 独自の動作をするエージェントを作成します。
class DialogueAgent(AgentBase):
    """
    簡単な応答を返す対話エージェント。
    `reply`メソッドをオーバーライド（再定義）して、独自の応答ロジックを実装します。
    """

    # `__init__`メソッドでエージェントの名前(name)と応答(response)を初期設定
    def __init__(self, name: str, response_text: str):
        # 親クラスである`AgentBase`の`__init__`を呼び出します。
        # AgentBaseのコンストラクタは引数を取りません。
        super().__init__()
        # nameはインスタンスの属性として直接設定します。
        self.name = name
        # このエージェントが返す固定の応答メッセージを保存します
        self.response_text = response_text

    async def reply(self, x: Msg) -> Msg:
        """
        エージェントがメッセージを受け取ったときに呼び出されるメソッド。
        AgentScopeフレームワークは、このメソッドが非同期(`async`)で定義されていることを期待します。
        引数 `x` には、他のエージェントから送信された`Msg`オブジェクトが入っています。

        このメソッドは、応答として新しい`Msg`オブジェクトを返す必要があります。
        """
        # 受け取ったメッセージをコンソールに表示
        print(f"[{self.name}]がメッセージを受信: '{x.content}'")

        # 自身の名前と、事前に設定された応答テキストを含む新しいメッセージを作成して返す
        # `role`は、このメッセージがどのような役割を持つかを示す重要な引数です。
        # ここではエージェントからの応答なので 'assistant' を指定します。
        response_msg = Msg(
            name=self.name,
            content=self.response_text,
            role="assistant",
        )
        return response_msg

# --- 3. エージェントの作成 ---
# 定義した`DialogueAgent`クラスから、2体のエージェントを実体化（インスタンス化）します。
print("2体のエージェントを作成します...")
agent_alice = DialogueAgent(
    name="アリス",
    response_text="こんにちは、ボブ！私はアリスです。",
)
agent_bob = DialogueAgent(
    name="ボブ",
    response_text="やあ、アリス！元気かい？",
)
print(f"エージェント '{agent_alice.name}' と '{agent_bob.name}' を作成しました。\n")


# --- 4. 対話の実行 ---
# AgentScopeのエージェント呼び出しは非同期処理です。
# そのため、`async def`で非同期関数を定義し、その中で対話を実行します。
async def main():
    """対話処理を実行するメインの非同期関数。"""
    print("--- 対話を開始します ---")

    # (1) 最初のメッセージを作成
    initial_msg = Msg(name="システム", content="アリスさん、ボブさんに挨拶してください。", role="system")
    print(f"[{initial_msg.name}]から送信: '{initial_msg.content}'")

    # (2) アリスが応答
    # エージェントの呼び出しはコルーチンを返すため、`await`キーワードを使って
    # 処理が完了するのを待ち、結果（応答メッセージ）を取得します。
    alice_response = await agent_alice(initial_msg)
    print(f"[{alice_response.name}]から送信: '{alice_response.content}'")

    # (3) ボブが応答
    # 同様に、ボブの応答も`await`で待ち受けます。
    bob_response = await agent_bob(alice_response)
    print(f"[{bob_response.name}]から送信: '{bob_response.content}'")

    print("\n--- 対話が終了しました ---")

# --- 5. 非同期関数の実行 ---
# Pythonで非同期関数を実行するための標準的な方法です。
# `if __name__ == "__main__":` のブロックで `asyncio.run()` を呼び出します。
if __name__ == "__main__":
    asyncio.run(main())

# 【まとめ】
# このように、AgentScopeでは `AgentBase` を継承して `reply` メソッドを実装することで
# エージェントの振る舞いを定義し、`Msg` オブジェクトをエージェント間で
# やり取りすることで対話が進行します。
#
# ★重要★
# エージェントの呼び出しは `await agent(...)` のように、非同期処理として
# 扱う必要があります。これはAgentScopeの基本設計です。
