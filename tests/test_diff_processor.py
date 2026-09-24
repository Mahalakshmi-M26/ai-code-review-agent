from app.scm.base import ChangedFile
from app.services.diff_processor import prepare_files


def test_diff_processor_skips_generated_and_binary_files():
    files = [ChangedFile("node_modules/x.js", "modified", "x"), ChangedFile("logo.png", "modified", "", True), ChangedFile("app.py", "modified", "x" * 20)]
    selected, skipped = prepare_files(files, max_files=2, max_file_chars=10, max_total_chars=100)
    assert [item.path for item in selected] == ["app.py"]
    assert selected[0].patch == "x" * 10
    assert skipped == 2
