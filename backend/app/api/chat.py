from fastapi import APIRouter
from sqlalchemy import select
from datetime import datetime
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

        # ----------------------------------------------------
        # Create or reuse conversation
        # ----------------------------------------------------

        if request.conversation_id is None:

            conversation = Conversation()

            db.add(conversation)
            db.commit()
            db.refresh(conversation)   #SQLAlchemy, go to the database, look at the row we just saved, and update my Python object with whatever is currently in that row.

            conversation_id = conversation.id

        else:
            conversation = db.get(
                Conversation,
                request.conversation_id
            )

            conversation.updated_at = datetime.utcnow()

            db.commit()

            conversation_id = conversation.id


        # ----------------------------------------------------
        # Save user message
        # ----------------------------------------------------

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        db.add(user_message)
        db.commit()


        # ----------------------------------------------------
        # Retrieve conversation history
        # ----------------------------------------------------

        messages = db.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at)
        ).scalars().all()


        chat_history = []

        recent_messages = (
            messages[-10:]
            if len(messages) > 10
            else messages
        )


        for message in recent_messages:

            if message.role == "user":

                chat_history.append(
                    HumanMessage(
                        content=message.content
                    )
                )

            elif message.role == "assistant":

                chat_history.append(
                    AIMessage(
                        content=message.content
                    )
                )


        # ----------------------------------------------------
        # Initial workflow state
        # ----------------------------------------------------

        initial_state: SupportState = {

            "user_message": request.message,

            "chat_history": chat_history,

            "intent": "",

            "order_id": "",

            "order_result": {},

            "knowledge_result": "",

            "refund_amount": 0.0,

            "refund_valid": False,

            "approval_required": False,

            "approval_status": "not_required",

            "final_response": ""
        }


        # ----------------------------------------------------
        # Run workflow
        # ----------------------------------------------------

        result = workflow.invoke(
            initial_state
        )


        response_text = result["final_response"]


        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=str(response_text)
        )

        db.add(assistant_message)
        db.commit()


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "conversation_id": conversation_id,
            "response": response_text
        }


    finally:

        db.close()