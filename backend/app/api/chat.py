from fastapi import APIRouter
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage

from backend.app.schemas.chat import ChatRequest
from backend.app.database.database import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.services.chat_service import get_ai_response

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
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

        # 3. Retrieve all messages from this conversation
        messages = db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).scalars().all()

        # 4. Convert database messages into LangChain messages (limiting context window for performance)
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

        # 5. Send conversation history to Gemini
        response = get_ai_response(chat_history)

        # 6. Save Gemini's response
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=str(response)
        )

        db.add(assistant_message)
        db.commit()

        # 7. Return response
        return {
            "conversation_id": conversation_id,
            "response": response
        }

    finally:
        db.close()