"""Generate the Week 4 RAG evaluation markdown report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def _resolve_repo_root() -> Path:
    module_path = Path(__file__).resolve()
    for ancestor in module_path.parents:
        if (ancestor / "docs").is_dir():
            return ancestor

    # Local monorepo layout: services/ai_engine/evaluation/report.py
    # Docker ai-service layout: /app/evaluation/report.py (ai_engine copied to /app)
    ai_engine_root = module_path.parents[1]
    return ai_engine_root.parent.parent


REPO_ROOT = _resolve_repo_root()
DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "evaluation_report.md"


def _format_score(value: float) -> str:
    return f"{value:.4f}"


def _format_latency(value: float) -> str:
    return f"{value:.2f} ms"


def render_evaluation_report(summary: dict) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# DocuBrain RAG Evaluation Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Overview",
        "",
        f"- Evaluated document: `{summary['source_document']}`",
        f"- Document ID: **{summary['document_id']}**",
        f"- Workspace ID: **{summary['workspace_id']}**",
        f"- Number of test questions: **{summary['num_questions']}**",
        f"- Overall Faithfulness: **{_format_score(summary['overall_faithfulness'])}**",
        f"- Overall Answer Relevance: **{_format_score(summary['overall_answer_relevancy'])}**",
        f"- Overall Context Recall: **{_format_score(summary['overall_context_recall'])}**",
        f"- Average latency: **{_format_latency(summary['average_latency_ms'])}**",
        "",
        "## Individual Results",
        "",
        "| ID | Question | Faithfulness | Answer Relevance | Context Recall | Latency |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]

    poor_questions = []

    for row in summary["questions"]:
        lines.append(
            "| {id} | {question} | {faithfulness} | {answer_relevancy} | {context_recall} | {latency} |".format(
                id=row["id"],
                question=row["question"].replace("|", "\\|"),
                faithfulness=_format_score(row["faithfulness"]),
                answer_relevancy=_format_score(row["answer_relevancy"]),
                context_recall=_format_score(row["context_recall"]),
                latency=_format_latency(row["latency_ms"]),
            )
        )

        if (
            row["faithfulness"] < 0.75
            or row["answer_relevancy"] < 0.75
            or row["context_recall"] < 0.75
        ):
            poor_questions.append(row)

    lines.extend(["", "## Question Details", ""])

    for row in summary["questions"]:
        lines.extend(
            [
                f"### Question {row['id']}",
                "",
                f"**Question:** {row['question']}",
                "",
                f"**Reference answer:** {row['reference_answer']}",
                "",
                f"**Generated answer:** {row['answer']}",
                "",
                f"**Latency:** {_format_latency(row['latency_ms'])}",
                "",
                f"**Faithfulness:** {_format_score(row['faithfulness'])}  ",
                f"**Answer Relevance:** {_format_score(row['answer_relevancy'])}  ",
                f"**Context Recall:** {_format_score(row['context_recall'])}",
                "",
                "**Retrieved contexts:**",
                "",
            ]
        )

        for index, context in enumerate(row["contexts"], start=1):
            lines.append(f"{index}. {context}")
            lines.append("")

    lines.extend(["## Poor Performers", ""])

    if not poor_questions:
        lines.append("No questions scored below 0.75 on any metric.")
    else:
        for row in poor_questions:
            lines.append(
                "- Question {id}: faithfulness={faithfulness}, "
                "answer_relevancy={answer_relevancy}, context_recall={context_recall}".format(
                    id=row["id"],
                    faithfulness=_format_score(row["faithfulness"]),
                    answer_relevancy=_format_score(row["answer_relevancy"]),
                    context_recall=_format_score(row["context_recall"]),
                )
            )

    lines.append("")
    return "\n".join(lines)


def write_evaluation_report(
    summary: dict,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_evaluation_report(summary), encoding="utf-8")
    return report_path
