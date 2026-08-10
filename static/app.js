/* 校园 AI 助手 —— 前端逻辑
 * 核心：把用户输入 POST 给后端 /api/chat，拿到回答渲染成气泡。
 * 每个浏览器一个 session_id（存在 localStorage），刷新页面记忆不丢。
 */

// ---------- 会话管理 ----------
const SESSION_KEY = "campus_session_id";
let sessionId = localStorage.getItem(SESSION_KEY) || "s_" + Math.random().toString(36).slice(2);
localStorage.setItem(SESSION_KEY, sessionId);

// ---------- DOM 元素 ----------
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");

// ---------- 渲染一条消息 ----------
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight; // 滚到底部
}

// ---------- 发送提问 ----------
async function send() {
  const question = input.value.trim();
  if (!question || sendBtn.disabled) return;

  appendMessage("user", question);
  input.value = "";
  sendBtn.disabled = true;

  // 先放一个"正在输入"占位，回答返回后替换
  appendMessage("assistant", "…");
  const typing = chatBox.lastElementChild;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, session_id: sessionId }),
    });
    const data = await res.json();
    typing.textContent = data.answer;
  } catch (e) {
    typing.textContent = "⚠️ 请求失败：" + e.message;
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ---------- 新对话：清空后端该会话的记忆 ----------
async function newChat() {
  await fetch("/api/chat/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  chatBox.innerHTML = ""; // 前端也清空
  appendMessage("assistant", "已开始新对话，有什么想问的？");
}

// ---------- 事件绑定 ----------
sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
newChatBtn.addEventListener("click", newChat);
