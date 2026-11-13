"""Run the fixed DocuBrain RAG evaluation dataset."""

from __future__ import annotations

import json
import time
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY
from evaluation.ragas_compat import load_ragas_evaluator
from evaluation.retrieval import contexts_as_strings, evaluation_vector_search

DATASET_PATH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "evaluation_dataset.json"


def _agent_system_prompt(workspace_id: int) -> str:
    return f"""
You are DocuBrain, a document question-answering assistant.

The current workspace ID is: {workspace_id}

Answer questions using the user's uploaded documents and
the available tools.

Use vector_search_tool for questions about document content.

Do not use outside knowledge.

Only answer the user's current question.

When a tool returns information, use only the information
needed to answer the current question.

If a tool cannot find the requested information, clearly
state that the information could not be found.
""".strip()


def load_evaluation_dataset(path: Path = DATASET_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_evaluation_answer(
    question: str,
    retrieved_results: list[dict],
    workspace_id: int,
) -> str:
    """
    Evaluation-only answer generation that mirrors the post-retrieval agent step
    without invoking LangGraph or changing production endpoints.
    """
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY,
        temperature=0.2,
    )

    context_text = "\n\n".join(
        f"[Page {result['page_number']}] {result['content']}"
        for result in retrieved_results
    )

    messages = [
        SystemMessage(content=_agent_system_prompt(workspace_id)),
        HumanMessage(
            content=(
                "Use only the retrieved document context below to answer the question.\n\n"
                f"Retrieved context:\n{context_text}\n\n"
                f"Question:\n{question}"
            )
        ),
    ]

    response = llm.invoke(messages)
    return response.content if isinstance(response.content, str) else str(response.content)


def run_rag_evaluation(dataset_path: Path = DATASET_PATH) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is required to run RAG evaluation.")

    dataset = load_evaluation_dataset(dataset_path)
    workspace_id = int(dataset["workspace_id"])
    document_id = int(dataset["document_id"])
    top_k = int(dataset["top_k"])

    question_rows = []

    for item in dataset["questions"]:
        started_at = time.perf_counter()

        retrieved_results = evaluation_vector_search(
            query=item["question"],
            workspace_id=workspace_id,
            document_id=document_id,
            top_k=top_k,
        )
        answer = generate_evaluation_answer(
            question=item["question"],
            retrieved_results=retrieved_results,
            workspace_id=workspace_id,
        )

        latency_ms = (time.perf_counter() - started_at) * 1000.0

        question_rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "reference_answer": item["reference_answer"],
                "answer": answer,
                "contexts": contexts_as_strings(retrieved_results),
                "retrieved_results": retrieved_results,
                "latency_ms": latency_ms,
            }
        )

    evaluate, Dataset, faithfulness, answer_relevancy, context_recall, llm, embeddings = (
        load_ragas_evaluator()
    )

    from ragas.run_config import RunConfig

    ragas_dataset = Dataset.from_dict(
        {
            "user_input": [row["question"] for row in question_rows],
            "response": [row["answer"] for row in question_rows],
            "retrieved_contexts": [row["contexts"] for row in question_rows],
            "reference": [row["reference_answer"] for row in question_rows],
        }
    )

    ragas_result = evaluate(
        ragas_dataset,
        metrics=[faithfulness, answer_relevancy, context_recall],
        llm=llm,
        embeddings=embeddings,
        run_config=RunConfig(timeout=600, max_workers=4),
        raise_exceptions=True,
    )

    scores_df = ragas_result.to_pandas()

    for index, row in enumerate(question_rows):
        row["faithfulness"] = float(scores_df.iloc[index]["faithfulness"])
        row["answer_relevancy"] = float(scores_df.iloc[index]["answer_relevancy"])
        row["context_recall"] = float(scores_df.iloc[index]["context_recall"])

    summary = {
        "source_document": dataset["source_document"],
        "document_id": document_id,
        "workspace_id": workspace_id,
        "num_questions": len(question_rows),
        "overall_faithfulness": float(scores_df["faithfulness"].mean()),
        "overall_answer_relevancy": float(scores_df["answer_relevancy"].mean()),
        "overall_context_recall": float(scores_df["context_recall"].mean()),
        "average_latency_ms": float(
            sum(row["latency_ms"] for row in question_rows) / len(question_rows)
        ),
        "questions": question_rows,
    }

    return summary
