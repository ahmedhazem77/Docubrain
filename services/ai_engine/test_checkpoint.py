from graph import graph


config = {
    "configurable": {
        "thread_id": "test-conversation-2"
    }
}


print("=== FIRST MESSAGE ===")

result1 = graph.invoke(
    {
        "query": "What is the main topic of the document?",
        "workspace_id": 1,
        "security_score": 0.0,
        "blocked": False,
        "messages": [
            {
                "role": "user",
                "content": "What is the main topic of the document?"
            }
        ]
    },
    config=config
)

print(result1)

print("\n=== SECOND MESSAGE ===")

result2 = graph.invoke(
    {
        "query": "What are its main challenges?",
        "workspace_id": 1,
        "security_score": 0.0,
        "blocked": False,
        "messages": [
            {
                "role": "user",
                "content": "What are its main challenges?"
            }
        ]
    },
    config=config
)

print(result2)

print("\n=== SAVED STATE ===")

state = graph.get_state(config)

print("Messages:")
for message in state.values["messages"]:
    print(message)