from backend.app.tools.available_tools import AVAILABLE_TOOLS


# Create a mapping:
# tool name → tool object
tools = {
    tool.name: tool
    for tool in AVAILABLE_TOOLS
}


def execute_tool(tool_call):
    tool_name = tool_call["name"]

    # Only execute tools that are in our approved tool list
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool = tools[tool_name]

    return tool.invoke(tool_call["args"])