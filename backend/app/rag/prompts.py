"""Prompt templates for the RAG system."""
from langchain_core.prompts import ChatPromptTemplate

# === 电商知识库助手 Prompt（已注释，待启用）===
# RAG_SYSTEM_PROMPT = """你是专业的电商产品知识库助手。你的知识全部来自内部产品资料。
#
# 回答规则：
# 1. 只能根据"参考信息"回答，禁止使用外部知识或编造信息
# 2. 信息不足以回答时，必须明确说"根据现有资料，我无法回答这个问题"
# 3. 回答中引用来源，使用 [Source-N] 格式标注（N 是来源编号）
# 4. 涉及产品参数、价格等数据时，务必准确引用原文，不篡改
# 5. 涉及多产品对比时，优先用表格呈现
# 6. 用中文回答，语言专业清晰，贴近电商客服风格"""

# 当前：中性模式，不限制模型身份
RAG_SYSTEM_PROMPT = ""

RAG_USER_PROMPT = """## 参考信息
{context}

## 对话历史
{history}

## 用户问题
{question}"""


def get_rag_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("user", RAG_USER_PROMPT),
        ]
    )
