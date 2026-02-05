import hashlib
from pathlib import Path


class Util:
    @classmethod
    def get_text_hex_prefix(cls, text: str, length: int = 8) -> str:
        md5 = hashlib.md5(text.encode('utf-8'))
        hex_digest = md5.hexdigest()
        return hex_digest[:length]

    @classmethod
    def read_text_file(cls, file_path: str, line: int | None = None) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            content = path.read_text()
            if line is None:
                return content
            lines = content.splitlines()
            if 1 <= line <= len(lines):
                return lines[line - 1]
            raise IndexError(
                f"Line {line} out of range for file with {len(lines)} lines.")
        except Exception as e:
            raise RuntimeError(f"Failed to read file {file_path}: {e}")
