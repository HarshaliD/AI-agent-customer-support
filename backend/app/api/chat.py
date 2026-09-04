from fastapi import APIRouter, Request
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage

from backend.app.schemas.chat import ChatRequest
from backend.app.database.database import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.services.chat_service import get_ai_response

from backend.app.rag.retrieval import retrieve_documents, build_context
from backend.app.rag.prompt import rag_prompt


router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest, http_request: Request):
    db = SessionLocal()

    try:
        # 1. Create a new conversation if this is the first message
        if request.conversation_id is None:
            conversation = Conversation()

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            conversation_id = conversation.id

        else:
            # Continue an existing conversation
            conversation_id = request.conversation_id

        # 2. Save the user's message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        db.add(user_message)
        db.commit()

        # 3. Retrieve conversation history
        messages = db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).scalars().all()

        # 4. Convert database messages into LangChain messages
        chat_history = []
        recent_messages = messages[-10:] if len(messages) > 10 else messages

        for message in recent_messages:
            if message.role == "user":
                chat_history.append(
                    HumanMessage(content=message.content)
                )

            elif message.role == "assistant":
                chat_history.append(
                    AIMessage(content=message.content)
                )

        # 5. Get the shared Chroma vector store
        vector_store = http_request.app.state.vector_store

        # 6. Retrieve relevant knowledge
        results = retrieve_documents(
            vector_store,
            request.message,
            k=2,
        )

        # 7. Build context from retrieved chunks
        context = build_context(results)

        # 8. Create the RAG prompt
        prompt = rag_prompt.invoke({
            "chat_history": chat_history,
            "context": context,
            "question": request.message,
        })

        # 9. Send prompt to Gemini
        response = get_ai_response([message for message in prompt.messages])

        # 10. Save Gemini's response
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=str(response)
        )

        db.add(assistant_message)
        db.commit()

        # 11. Return response
        return {
            "conversation_id": conversation_id,
            "response": response
        }

    finally:
        db.close()