from fastapi import APIRouter
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage

from backend.app.schemas.chat import ChatRequest
from backend.app.schemas.workflow import SupportState

from backend.app.database.database import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message

from backend.app.agents.workflow import workflow


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

        # 3. Retrieve conversation history
        messages = db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).scalars().all()

        # 4. Convert database messages into LangChain messages
        chat_history = []

        recent_messages = (
            messages[-10:]
            if len(messages) > 10
            else messages
        )

        for message in recent_messages:

            if message.role == "user":
                chat_history.append(
                    HumanMessage(content=message.content)
                )

            elif message.role == "assistant":
                chat_history.append(
                    AIMessage(content=message.content)
                )

        # 5. Create the initial workflow state
        initial_state: SupportState = {
            "user_message": request.message,
            "chat_history": chat_history,
            "intent": "",
            "order_id": "",
            "order_result": {},
            "knowledge_result": "",
            "final_response": ""
        }
        # 6. Run the LangGraph workflow
        result = workflow.invoke(initial_state)

        # 7. Extract the final response
        response_text = result["final_response"]

        # 8. Save assistant response
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=str(response_text)
        )

        db.add(assistant_message)
        db.commit()

        # 9. Return response to frontend
        return {
            "conversation_id": conversation_id,
            "response": response_text
        }

    finally:
        db.close()