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

        # ====================================================
        # 1. GET OR CREATE CONVERSATION
        # ====================================================

        if request.conversation_id is None:

            conversation = Conversation()

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            conversation_id = conversation.id

        else:

            conversation = db.get(
                Conversation,
                request.conversation_id
            )

            if conversation is None:
                return {
                    "error": "Conversation not found."
                }

            conversation.updated_at = datetime.utcnow()

            db.commit()

            conversation_id = conversation.id


        # ====================================================
        # 2. SAVE USER MESSAGE
        # ====================================================

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        db.add(user_message)
        db.commit()


        # ====================================================
        # 3. GET CONVERSATION HISTORY
        # ====================================================

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


        # ====================================================
        # 4. CREATE INITIAL WORKFLOW STATE
        # ====================================================

        initial_state: SupportState = {
            "conversation_id": conversation_id,

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

            # Load persistent cancellation state
            # from the Conversation table.
            "pending_action": conversation.pending_action,

            "pending_order_id": conversation.pending_order_id,

            "user_confirmation": None,

            "final_response": ""
        }


        # ====================================================
        # 5. RUN WORKFLOW
        # ====================================================

        result = workflow.invoke(
            initial_state
        )


        response_text = result["final_response"]

        # ====================================================
        # 6. SAVE UPDATED PENDING STATE
        # ====================================================

        conversation.pending_action = (
            result["pending_action"]
        )

        conversation.pending_order_id = (
            result["pending_order_id"]
        )

        conversation.updated_at = datetime.utcnow()

        db.commit()

        # ====================================================
        # 7. SAVE ASSISTANT RESPONSE
        # ====================================================

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=str(response_text)
        )

        db.add(assistant_message)

        db.commit()


        # ====================================================
        # 8. RETURN RESPONSE
        # ====================================================

        return {
            "conversation_id": conversation_id,
            "response": response_text
        }


    finally:

        # Always close the SQLAlchemy session.
        db.close()