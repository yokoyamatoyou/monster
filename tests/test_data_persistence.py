import sys
from pathlib import Path
import csv

sys.path.append(str(Path(__file__).resolve().parents[1]))

import data_persistence


def test_save_interaction(tmp_path, monkeypatch):
    path = tmp_path / "test.csv"
    monkeypatch.setattr(data_persistence, "CSV_PATH", path)
    data_persistence.save_interaction(
        user_id="u", question_text="q", answer_text="a",
        total_question_count=1, evaluation_summary="s"
    )
    assert path.exists()
    rows = list(csv.DictReader(path.open()))
    assert rows[0]["user_id"] == "u"
    assert rows[0]["evaluation_summary"] == "s"
