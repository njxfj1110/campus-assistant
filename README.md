# 🎓 校园 AI 助手

一个基于 **RAG（检索增强生成）** 的校园办事问答助手。把你的学校官网公开文档放进 `knowledge_base/`，它就能回答新生/在校生的日常问题——报到要带什么材料、怎么选课、宿舍几点熄灯、图书馆怎么借书……

> 当前 `knowledge_base/` 是**通用示例数据**，用于跑通框架。换成你学校的真实文档即可落地。

## ✨ 功能

- 💬 网页聊天界面，打开浏览器直接用
- 📚 **RAG 检索增强**：回答前先从知识库检索相关段落，强约束模型"引用原文、不编造"
- 🧠 **会话记忆**：多会话隔离，刷新页面上下文不丢，可一键"新对话"
- 🚢 **Docker 一键部署**，可上云服务器对外提供服务

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python + FastAPI |
| LLM | DeepSeek（OpenAI 兼容接口，可换任意 OpenAI 兼容模型） |
| 检索 | 关键词匹配（v1）→ 计划升级语义向量 |
| 前端 | 原生 HTML + CSS + JavaScript |
| 部署 | Docker |

## 📁 项目结构

```
campus-assistant/
├── app/
│   ├── main.py          # FastAPI 入口与接口
│   ├── agent.py         # 问答闭环：检索→拼prompt→调LLM→回答
│   ├── retriever.py     # 知识库检索
│   └── memory.py        # 会话记忆（滑动窗口）
├── static/              # 前端页面（html/css/js）
├── knowledge_base/      # 知识库文档（换成你的真实数据）
├── requirements.txt
├── Dockerfile
└── .env.example         # 配置模板
```

## 🚀 本地运行

```bash
# 1. 配密钥
cp .env.example .env   # 填入你的 LLM_API_KEY

# 2. 建环境、装依赖
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt

# 3. 启动
.venv/Scripts/uvicorn app.main:app --reload
```

浏览器打开 http://127.0.0.1:8000 即可对话。

## 🐳 Docker 部署

```bash
docker build -t campus-assistant .
docker run -d -p 8000:8000 --env-file .env --name campus campus-assistant
```

然后访问 http://服务器IP:8000（云服务器需在安全组放行 8000 端口）。

## 🔄 迭代路线

- [x] v1.0 关键词 RAG + 网页聊天 + Docker 部署
- [ ] v1.1 语义检索（sentence-transformers），答案更准
- [ ] v1.2 会话持久化 + 访问统计
- [ ] v1.3 多 Agent 优化 + 评测集
- [ ] v1.4 用户反馈闭环（点赞/踩 + 错答日志）

## 📝 更新知识库

把学校官网（教务处 / 学工部 / 图书馆 / 后勤）的办事指南、常见问题，整理成 `txt`/`md` 文件放进 `knowledge_base/` 即可。建议一个主题一个文件，命名用中文。

---

*示例数据仅供演示，请替换为真实信息。*
