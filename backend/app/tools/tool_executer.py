import json

from backend.app.tools.available_tools import AVAILABLE_TOOLS
from backend.app.database.database import SessionLocal
from backend.app.models.agent_action import AgentAction


# Create a mapping:
# tool name → tool object
tools = {
    tool.name: tool
    for tool in AVAILABLE_TOOLS
}


def execute_tool(tool_call, conversation_id):
    tool_name = tool_call["name"]

    # Only execute tools that are in our approved tool list
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool = tools[tool_name]
    arguments = tool_call["args"]

    db = SessionLocal()

    try:
        # Execute the actual tool
        result = tool.invoke(arguments)

        # Save the successful action
        action = AgentAction(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments=json.dumps(arguments),
            result=str(result),
            status="success"
        )

        db.add(action)
        db.commit()

        return result

    except Exception as e:
        # Save the failed action
        action = AgentAction(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments=json.dumps(arguments),
            result=str(e),
            status="error"
        )

        db.add(action)
        db.commit()

        raise

    finally:
        db.close()