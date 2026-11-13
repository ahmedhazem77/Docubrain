from typing import Annotated, TypedDict
import re
import uuid
from opentelemetry import trace
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from config import DATABASE_URL, GROQ_API_KEY, groq_client
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from tools import (
    vector_search_tool,
    workspace_stats_tool,
    document_summarizer_tool,
    resolve_document_id_by_filename,
)


tracer = trace.get_tracer(__name__)


# AGENT LLM

agent_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.2
)

agent_llm_with_tools = agent_llm.bind_tools(
    [
        vector_search_tool,
        workspace_stats_tool,
        document_summarizer_tool

    ]
)



# GRAPH STATE

class AgentState(TypedDict):
    query: str
    workspace_id: int
    security_score: float
    blocked: bool
    messages: Annotated[list, add_messages]


# SECURITY NODE

def security_node(state: AgentState):

    print("Security node received:", state["query"])

    with tracer.start_as_current_span("security_guardrail") as span:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-prompt-guard-2-22m",
            messages=[
                {
                    "role": "user",
                    "content": state["query"]
                }
            ]
        )

        security_score = float(
            response.choices[0].message.content   #Get the model's output
        )

        blocked = security_score >= 0.5
        span.set_attribute("security.score", security_score)
        span.set_attribute("security.blocked", blocked)

    print("Security score:", security_score)

    return {
        "security_score": security_score,
        "blocked": blocked,
    }


# AGENT NODE

def _extract_summarize_filename(query: str) -> str | None:
    match = re.match(r"(?i)^\s*summarize\s+(.+)\s*$", query.strip())  # summarize <filename> (case-insensitive, allows leading/trailing whitespace)

    if not match:
        return None

    filename = match.group(1).strip()

    if len(filename) >= 2 and filename[0] == filename[-1] and filename[0] in "\"'":
        filename = filename[1:-1].strip()

    return filename or None


_CONVERSATIONAL_QUERY_PATTERN = re.compile(
    r"(?i)^\s*(?:"
    r"hi|hello|hey|"
    r"thanks|thank you|"
    r"good morning|good afternoon|good evening|"
    r"how are you"
    r")[\s!.?]*$"
)


def _is_conversational_query(query: str) -> bool:
    return bool(_CONVERSATIONAL_QUERY_PATTERN.match(query.strip()))     # check wether we are simply having a converstaion without asking for any document related information


def agent_node(state: AgentState):

    system_message = SystemMessage(
        content=f"""
You are DocuBrain, a document question-answering assistant.

The current workspace ID is: {state["workspace_id"]}

Answer questions using the user's uploaded documents and
the available tools.

Use vector_search_tool for questions about document content.

Use workspace_stats_tool for questions about workspace
metadata such as document counts, upload dates, and statuses.

Use document_summarizer_tool when the user explicitly asks
for a summary of a specific document.

When calling a tool that requires workspace_id, ALWAYS use
the current workspace ID: {state["workspace_id"]}

Do not use a different workspace ID.

Do not use outside knowledge.

Only answer the user's current question.

Do not include information from previous questions or tool
results unless that information is directly relevant to
the current question.

Do not combine answers to multiple questions unless the
user explicitly asks you to do so.

When a tool returns information, use only the information
needed to answer the current question.

If a tool cannot find the requested information, clearly
state that the information could not be found.
"""
    )

    messages = state["messages"]   #retrieve the messages from the state(conversation history)
    last_message = messages[-1] if messages else None  # get mostrecent message 

    if not isinstance(last_message, ToolMessage): # check if the last message is a tool message
        summarize_filename = _extract_summarize_filename(state["query"])  #call helper function to extract filename if the user is asking for a summary of a document

        if summarize_filename is not None:  # check wether the file name exists
            document_id = resolve_document_id_by_filename(
                state["workspace_id"],
                summarize_filename,
            )

            if document_id is not None:
                return {
                    "messages": [
                        AIMessage(
                            content="",
                            tool_calls=[
                                {
                                    "name": "document_summarizer_tool",
                                    "args": {"document_id": document_id},
                                    "id": f"summarize-{document_id}-{uuid.uuid4().hex[:8]}",
                                }
                            ],
                        )
                    ]
                }

        if not _is_conversational_query(state["query"]):
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "vector_search_tool",
                                "args": {
                                    "query": state["query"],
                                    "workspace_id": state["workspace_id"],
                                    "top_k": 4,
                                },
                                "id": f"vector-search-{uuid.uuid4().hex[:8]}",
                            }
                        ],
                    )
                ]
            }

    messages = [
        system_message,
        *state["messages"]
    ]

    response = agent_llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

# TOOL NODE

tool_node = ToolNode(
    [
        vector_search_tool,
        workspace_stats_tool,
        document_summarizer_tool
    ]
)


# ROUTING

def route_after_security(state: AgentState):

    if state["blocked"]:
        return "blocked"

    return "safe"


def route_after_agent(state: AgentState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return "end"


# BUILD GRAPH

graph_builder = StateGraph(AgentState)


graph_builder.add_node(
    "security",
    security_node
)

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    tool_node
)


# START → SECURITY

graph_builder.add_edge(
    START,
    "security"
)


# SECURITY → AGENT or END

graph_builder.add_conditional_edges(
    "security",
    route_after_security,
    {
        "blocked": END,
        "safe": "agent"
    }
)


# AGENT → TOOLS or END

graph_builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "end": END
    }
)


# TOOLS → AGENT

graph_builder.add_edge(
    "tools",
    "agent"
)

# POSTGRESQL CHECKPOINTER

checkpointer_context = PostgresSaver.from_conn_string(
    DATABASE_URL
)

checkpointer = checkpointer_context.__enter__()

# COMPILE GRAPH

graph = graph_builder.compile(
    checkpointer=checkpointer
)