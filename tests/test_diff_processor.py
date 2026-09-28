from app.models import ChangedFile
from app.reviewer import annotate_changed_lines, prepare_files


def test_diff_processor_skips_generated_and_binary_files():
    files = [ChangedFile("node_modules/x.js", "modified", "x"), ChangedFile("logo.png", "modified", "", True), ChangedFile("app.py", "modified", "x" * 20)]
    selected, skipped = prepare_files(files, max_files=2, max_file_chars=10, max_total_chars=100)
    assert [item.path for item in selected] == ["app.py"]
    assert selected[0].patch == "x" * 10
    assert skipped == 2


def test_patch_annotation_numbers_added_new_file_lines_only():
    patch = "\n".join([
        "@@ -75,3 +79,4 @@ def get_pet_names(pets):",
        "     names = []",
        '-    names.append(pet["label"])',
        "+    for pet in pets:",
        '+        names.append(pet["name"])',
        "     return names",
        "@@ -100,1 +102,0 @@",
        "-removed_only()",
        "@@ -110,1 +112,1 @@",
        "---legacy",
        "+++replacement",
    ])
    annotated, changed_lines = annotate_changed_lines(patch)

    assert "+80:     for pet in pets" in annotated
    assert '+81:         names.append(pet["name"])' in annotated
    assert '-    names.append(pet["label"])' in annotated
    assert "-removed_only()" in annotated
    assert "+112: ++replacement" in annotated
    assert changed_lines == {80, 81, 112}
