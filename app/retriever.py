"""retriever.py — 知识库检索（关键词匹配 v1）

流程：读 knowledge_base/ 所有文档 → 按句号切成段落 → 把问题里的每个字符
去段落里数出现次数（字符频率匹配）→ 得分最高的前 top_k 段返回。

这个检索很"笨"，但简单可靠、零依赖、跑得快——先用它把产品跑上线。
升级预告（v1.1）：换成 sentence-transformers 语义向量检索，答案会更准。
"""

from pathlib import Path

# knowledge_base 在项目根目录（app/ 的上一级）
KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"


def load_paragraphs() -> list[str]:
    """读取知识库里所有文档，按句号切成段落，返回段落列表"""
    paragraphs = []
    for path in sorted(KB_DIR.glob("*.txt")) + sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for para in text.split("。"):
            para = para.strip()
            if para:
                paragraphs.append(para + "。")
    return paragraphs


# 模块加载时读一次，之后复用（改文档要重启服务才生效）
PARAGRAPHS = load_paragraphs()


def _score(question: str, para: str) -> int:
    """相关度：问题里每个字符在段落里出现次数之和"""
    total = 0
    for ch in question:
        if ch.strip():
            total += para.count(ch)
    return total


def retrieve(question: str, top_k: int = 3) -> list[str]:
    """给每个段落打分，取分数最高且非零的前 top_k 段"""
    scored = [(_score(question, p), p) for p in PARAGRAPHS]
    scored.sort(reverse=True)
    hits = [p for s, p in scored if s > 0]
    return hits[:top_k]
