"""agent.py — 问答闭环：检索 → 拼 prompt → 调 LLM → 回答

和 hello-agents 的 agent_loop 同款思路，v1 做了减法：
不带工具调用，专注"查知识库 + 回答"，先把产品跑通上线。

核心流程（记住这个顺序，面试要能讲）：
    用户问题 → ① 存进会话历史
           → ② 从知识库检索相关段落
           → ③ 动态拼 system prompt（原指令 + 知识库参考，强约束不准编造）
           → ④ 把 system + 历史 一起发给模型
           → ⑤ 模型回答 → 存进会话历史 → 返回
"""

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from .memory import add_user, add_assistant, get_history
from .retriever import retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s[%(levelname)s] %(message)s")

load_dotenv()
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

# ---------- 基础系统提示词（三段式：角色 / 任务规则 / 输出要求） ----------
SYSTEM_PROMPT = """
# 角色设定
你是一个熟悉大学校园生活的 AI 助手，专门回答新生和在校生关于校园办事的问题。

# 任务规则
1. 回答必须依据"知识库参考"里的权威信息，直接引用原文，不要编造
2. 知识库里没有提到的，如实说明"这部分我暂时没有资料，建议咨询学校相关部门"
3. 步骤型问题（怎么办、怎么带）用分条列出，方便用户照着做

# 输出要求
- 使用中文，简洁清晰
- 提到时间、地点、材料时，以知识库原文为准
"""


def chat(session_id: str, question: str) -> str:
    # ① 用户问题先进历史
    add_user(session_id, question)

    # ② 检索知识库，拿到相关段落
    context = retrieve(question)
    context_block = "\n".join(f"- {p}" for p in context)

    # ③ 动态拼 system prompt：基础指令 + 知识库参考（强约束）
    if context_block:
        system_prompt = SYSTEM_PROMPT + f"""

# 知识库参考 —— 以下是权威事实来源

规则：
1. 回答必须以上述段落为依据，直接引用原文表述
2. 不要用自己的常识替换或补充段落内容
3. 段落能回答的问题，直接给出答案，不要长篇展开
4. 段落没有提到的事实，不要编造

{context_block}
"""
    else:
        system_prompt = SYSTEM_PROMPT

    # ④ 组装消息：system 在前，会话历史在后（含刚加入的用户问题）
    messages = [
        {"role": "system", "content": system_prompt},
        *get_history(session_id),
    ]

    logging.info(f"[{session_id}] 提问: {question}")

    # ⑤ 调模型
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=messages,
    )
    answer = response.choices[0].message.content

    # ⑥ 回答进历史，返回
    add_assistant(session_id, answer)
    return answer
