from langchain_core.messages import HumanMessage, ToolMessage

from backend.app.services.chat_service import model
from backend.app.tools.available_tools import AVAILABLE_TOOLS
from backend.app.tools.tool_executer import execute_tool


# Give Gemini all approved tools
model_with_tools = model.bind_tools(AVAILABLE_TOOLS)


user_message = HumanMessage(
    content="What is NovaMart's return policy?"
)

messages = [user_message]


while True:
    # Ask Gemini what to do next
    response = model_with_tools.invoke(messages)

    print("\nGemini response:")
    print(response)

    # If Gemini doesn't request a tool,
    # it has produced the final answer.
    if not response.tool_calls:
        break

    # Add Gemini's tool request to the conversation
    messages.append(response)

    # Execute every tool requested by Gemini
    for tool_call in response.tool_calls:

        print("\nRequested tool:", tool_call["name"])
        print("Tool arguments:", tool_call["args"])

        # Application executes the approved tool
        tool_result = execute_tool(tool_call)

        print("Tool result:")
        print(tool_result)

        # Send the tool result back to Gemini
        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            )
        )


print("\nFinal response:")
print(response.content)

fake_tool_call = {
    "name": "delete_customer",
    "args": {
        "customer_id": "CUS-001"
    }
}

try:
    result = execute_tool(fake_tool_call)
    print(result)
except ValueError as e:
    print("Rejected:", e)