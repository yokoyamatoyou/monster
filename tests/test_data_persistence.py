import sys
from pathlib import Path
import csv

sys.path.append(str(Path(__file__).resolve().parents[1]))

import data_persistence


def test_save_interaction(tmp_path, monkeypatch):
    path = tmp_path / "test.csv"
    monkeypatch.setattr(data_persistence, "CSV_PATH", path)
    monkeypatch.setattr(data_persistence, "USERS_PATH", tmp_path / "users.csv")
    ts = "2024-01-01T00:00:00+00:00"
    data_persistence.save_interaction(
        user_id="u", question_text="q", answer_text="a",
        total_question_count=1, evaluation_summary="s", start_timestamp=ts
    )
    assert path.exists()
    rows = list(csv.DictReader(path.open()))
    assert rows[0]["user_id"] == "u"
    assert rows[0]["evaluation_summary"] == "s"
    assert rows[0]["timestamp"] == ts


def test_save_and_get_user(tmp_path, monkeypatch):
    users = tmp_path / "users.csv"
    monkeypatch.setattr(data_persistence, "USERS_PATH", users)
    data_persistence.save_user("abc", "Taro")
    assert users.exists()
    assert data_persistence.get_user_name("abc") == "Taro"
    # Saving again should not duplicate
    data_persistence.save_user("abc", "Taro")
    rows = list(csv.DictReader(users.open()))
    assert len(rows) == 1
