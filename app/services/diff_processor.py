from app.scm.base import ChangedFile

IGNORED_PARTS = {"node_modules", "dist", "build", "coverage", ".git"}
IGNORED_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}


def prepare_files(files: list[ChangedFile], max_files: int, max_file_chars: int, max_total_chars: int) -> tuple[list[ChangedFile], int]:
    selected: list[ChangedFile] = []
    skipped = 0
    total = 0
    for item in files:
        parts = set(item.path.replace("\\", "/").split("/"))
        if item.binary or item.path.split("/")[-1] in IGNORED_NAMES or parts & IGNORED_PARTS:
            skipped += 1
            continue
        if len(selected) >= max_files or total >= max_total_chars:
            skipped += 1
            continue
        item.patch = item.patch[:max_file_chars]
        selected.append(item)
        total += len(item.patch)
    return selected, skipped
