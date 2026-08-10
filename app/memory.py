"""memory.py — 会话记忆（按 session 隔离，滑动窗口版）

v1 做法：后端用字典 {session_id: 消息列表}，每个浏览器会话的记忆互相独立。
每个会话最多保留 MAX_ITEMS 条，超出的丢掉最旧的，防止 token 越聊越贵。

升级预告（v1.2）：目前存在进程内存里，重启即清空；
上线多人后可以换成 Redis 或数据库。
"""

MAX_ITEMS = 10

# 所有会话的历史：{session_id: [{"role": "user"/"assistant", "content": ...}, ...]}
sessions = {}


def get_history(session_id: str) -> list[dict]:
    """取某会话的历史列表；没有就创建空的"""
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]


def _trim(history: list[dict]):
    """滑动窗口：超上限就从最前面（最旧）丢掉"""
    while len(history) > MAX_ITEMS:
        history.pop(0)


def add_user(session_id: str, text: str):
    h = get_history(session_id)
    h.append({"role": "user", "content": text})
    _trim(h)


def add_assistant(session_id: str, text: str):
    h = get_history(session_id)
    h.append({"role": "assistant", "content": text})
    _trim(h)


def reset(session_id: str):
    """清空某会话（前端可加"新对话"按钮调这个）"""
    sessions.pop(session_id, None)
