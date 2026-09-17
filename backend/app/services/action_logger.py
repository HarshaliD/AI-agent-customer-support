import json
import time

from backend.app.database.database import SessionLocal
from backend.app.models.agent_action import AgentAction


def execute_and_log_tool(
    tool,
    arguments,
    conversation_id
):
    """
    Execute a tool and record the action in agent_actions.
    """

    start_time = time.perf_counter()

    try:
        # Execute the actual tool
        result = tool.invoke(arguments)

        latency = time.perf_counter() - start_time

        # Some tools return an error dictionary
        # instead of raising an exception.
        if isinstance(result, dict) and "error" in result:
            status = "error"
        else:
            status = "success"

        # Record the action
        db = SessionLocal()

        action = AgentAction(
            conversation_id=conversation_id,
            tool_name=tool.name,
            arguments=json.dumps(arguments),
            result=str(result),
            status=status,
            latency=latency
        )

        db.add(action)
        db.commit()
        db.close()

        print(
            f"[OBSERVABILITY] "
            f"{tool.name} | {status} | {latency:.3f}s"
        )

        return result

    except Exception as e:

        latency = time.perf_counter() - start_time

        # Record unexpected execution failure
        db = SessionLocal()

        action = AgentAction(
            conversation_id=conversation_id,
            tool_name=tool.name,
            arguments=json.dumps(arguments),
            result=str(e),
            status="error",
            latency=latency
        )

        db.add(action)
        db.commit()
        db.close()

        print(
            f"[OBSERVABILITY] "
            f"{tool.name} | error | {latency:.3f}s"
        )

        raise