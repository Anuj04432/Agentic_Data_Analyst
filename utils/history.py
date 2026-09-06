from pathlib import Path


def save_history(file):
    UPLOAD_DIR =  Path("data/history/")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if file:
        file_path = UPLOAD_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

def get_history():
    UPLOAD_DIR = Path("data/history/")
    if not UPLOAD_DIR.exists():
        return []
    return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
