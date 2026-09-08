from backend.app.tools.knowledge_tools import search_knowledge_base


result = search_knowledge_base.invoke({
    "query": "What is NovaMart's return policy?"
})

print("Knowledge tool result:")
print(result)