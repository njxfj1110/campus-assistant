# 校园 AI 助手 —— 镜像配方
# 每行指令 = 镜像的一层，构建时从上往下执行
FROM python:3.12-slim

WORKDIR /app

# 先装依赖（单独一层，改代码不用重装）
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再拷项目（含 app/ static/ knowledge_base/）
COPY . .

EXPOSE 8000

# 监听所有网卡，容器外才能访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
