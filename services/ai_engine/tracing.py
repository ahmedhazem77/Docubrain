"""
Phoenix / OpenInference tracing bootstrap for the AI engine.

Import this module before LangChain-backed modules (graph, tools) so
LangChainInstrumentor wraps ChatGroq invocations such as agent_llm and
summarizer_llm.
"""
import os

_initialized = False


def setup_tracing() -> None:
    global _initialized

    if _initialized:
        return

    enabled = os.getenv("PHOENIX_TRACING_ENABLED", "true").strip().lower()
    if enabled in {"0", "false", "no", "off"}:
        _initialized = True
        return

    collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
    if not collector_endpoint:
        _initialized = True
        return

    from phoenix.otel import register
    from openinference.instrumentation.langchain import LangChainInstrumentor

    tracer_provider = register(
        project_name=os.getenv("PHOENIX_PROJECT_NAME", "docubrain"),
        endpoint=collector_endpoint,
        batch=True,
        auto_instrument=False,
    )

    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

    _initialized = True


setup_tracing()
