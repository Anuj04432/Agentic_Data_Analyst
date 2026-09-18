from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploaded"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
HISTORY_DIR = PROJECT_ROOT / "utils" / "saved_history"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True,exist_ok=True)

def save_history(file) -> Path:
    if file:
        file_path = UPLOAD_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        if hasattr(file,"seek"):
            file.seek(0)
        return file_path
    return None


def get_history() -> list[str]:
    datasets = set()
    for dir in  [SAMPLE_DIR,UPLOAD_DIR,HISTORY_DIR]:
        if dir.exists():
            for f in dir.iterdir():
                if f.is_file() and not f.name.startswith(".") and f.name != ".gitkeep":
                    datasets.add(f.name)
    return sorted(list(datasets))


def get_file_path(filename: str) -> Path:
    for dir in [UPLOAD_DIR, SAMPLE_DIR, HISTORY_DIR]:
        candidate = dir/filename
        if candidate.exists() and candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Dataset '{filename}' not found in the data directories ")
