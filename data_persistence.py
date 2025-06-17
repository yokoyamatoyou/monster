"""Utilities for saving interaction data to CSV."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "interactions.csv"


COLUMNS = [
    "timestamp",
    "user_id",
    "question_text",
    "answer_text",
    "total_question_count",
    "evaluation_summary",
]


def save_interaction(
    user_id: str,
    question_text: str,
    answer_text: str,
    total_question_count: int,
    evaluation_summary: str,
) -> None:
    """Append a single interaction row to the CSV file."""
    new_file = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "question_text": question_text,
                "answer_text": answer_text,
                "total_question_count": total_question_count,
                "evaluation_summary": evaluation_summary,
            }
        )
