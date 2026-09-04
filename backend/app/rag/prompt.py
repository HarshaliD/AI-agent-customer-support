from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a customer support assistant for NovaMart.

Use the retrieved knowledge to answer the customer's question.

Retrieved knowledge:
{context}
"""
    ),

    MessagesPlaceholder("chat_history"),

    (
        "human",
        "{question}"
    ),
])