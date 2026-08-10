"""main.py — FastAPI 入口：一个聊天接口 + 一个静态前端

启动方式（在项目根目录）：
    .venv/Scripts/uvicorn app.main:app --reload
浏览器打开 http://127.0.0.1:8000 即可使用。

接口：
    POST /api/chat   {"question": "...", "session_id": "..."} → {"answer": "...", "session_id": "..."}
    GET  /           返回聊天页面（static/index.html）
    /static/...      前端静态资源
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .agent import chat
from .memory import reset as reset_memory

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="校园 AI 助手")


# ---------- 请求 / 响应 数据模型 ----------
class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"  # 不传就用默认会话


class ChatResponse(BaseModel):
    answer: str
    session_id: str


# ---------- 接口 ----------
@app.get("/")
def index():
    """根路径返回聊天页面"""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/chat")
def api_chat(req: ChatRequest) -> ChatResponse:
    """核心接口：提问 → 检索 + LLM 回答"""
    answer = chat(req.session_id, req.question)
    return ChatResponse(answer=answer, session_id=req.session_id)


@app.post("/api/chat/reset")
def reset_chat(req: ChatRequest) -> ChatResponse:
    """清空某会话记忆（前端"新对话"按钮用）"""
    reset_memory(req.session_id)
    return ChatResponse(answer="", session_id=req.session_id)


# 挂载静态资源（前端 css / js）
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
