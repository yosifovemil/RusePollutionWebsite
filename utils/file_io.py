from pathlib import Path


def read_file(file: Path):
    f = file.open()
    content = f.read()
    f.close()
    return content
