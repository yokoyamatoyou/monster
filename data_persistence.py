"""Utilities for saving interaction data to CSV."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "interactions.csv"
USERS_PATH = DATA_DIR / "users.csv"


COLUMNS = [
    "timestamp",
    "user_id",
    "question_text",
    "answer_text",
    "total_question_count",
    "evaluation_summary",
]

USER_COLUMNS = ["user_id", "user_name"]


def save_interaction(
    user_id: str,
    question_text: str,
    answer_text: str,
    total_question_count: int,
    evaluation_summary: str,
    start_timestamp: str | None = None,
) -> None:
    """Append a single interaction row to the CSV file."""
    ts = start_timestamp or datetime.now(timezone.utc).isoformat()
    new_file = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": ts,
                "user_id": user_id,
                "question_text": question_text,
                "answer_text": answer_text,
                "total_question_count": total_question_count,
                "evaluation_summary": evaluation_summary,
            }
        )


def save_user(user_id: str, user_name: str) -> None:
    """Persist user ID and name mapping if not already stored."""
    new_file = not USERS_PATH.exists()
    users: dict[str, str] = {}
    if USERS_PATH.exists():
        with USERS_PATH.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                users[row["user_id"]] = row["user_name"]
    if user_id in users:
        return
    with USERS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=USER_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow({"user_id": user_id, "user_name": user_name})


def get_user_name(user_id: str) -> str | None:
    """Return stored user name for ID if available."""
    if not USERS_PATH.exists():
        return None
    with USERS_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["user_id"] == user_id:
                return row["user_name"]
    return None


def get_question_history(user_id: str) -> list[str]:
    """Return list of past question texts for the given user."""
    if not CSV_PATH.exists():
        return []
    history: list[str] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["user_id"] == user_id:
                history.append(row["question_text"])
    return history
