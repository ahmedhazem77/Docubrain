import os

import pytest

from config import DATABASE_URL
from evaluation.report import DEFAULT_REPORT_PATH, write_evaluation_report
from evaluation.runner import run_rag_evaluation


@pytest.mark.evaluation
def test_rag_evaluation_generates_report():
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY is required for RAG evaluation.")

    if not DATABASE_URL:
        pytest.skip("DATABASE_URL is required for PostgreSQL-backed RAG evaluation.")

    summary = run_rag_evaluation()

    assert summary["num_questions"] == 10
    assert len(summary["questions"]) == 10
    assert summary["source_document"] == "finalReport(final).pdf"
    assert summary["document_id"] == 2
    assert summary["workspace_id"] == 1

    report_path = write_evaluation_report(summary, DEFAULT_REPORT_PATH)

    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "Overall Faithfulness" in report_text
    assert "Overall Answer Relevance" in report_text
    assert "Overall Context Recall" in report_text
    assert "Average latency" in report_text
    assert "Document ID" in report_text
    assert "Workspace ID" in report_text
