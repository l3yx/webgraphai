import hashlib
from pathlib import Path
import difflib


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

    def get_text_update(
        cls,
        old_text: str,
        new_text: str,
        threshold_ratio: float = 0.75,
        context_lines: int = 4,
        compact: bool = False
    ) -> dict:
        old_lines = old_text.splitlines(keepends=False)
        new_lines = new_text.splitlines(keepends=False)
        if compact:
            diff_lines = list(difflib.ndiff(
                [line + '\n' for line in old_lines],
                [line + '\n' for line in new_lines]
            ))
            changed_indices = set()
            for i, line in enumerate(diff_lines):
                if line.startswith('+ ') or line.startswith('- '):
                    for j in range(max(0, i - context_lines), min(len(diff_lines), i + context_lines + 1)):
                        changed_indices.add(j)
            if not changed_indices:
                return {
                    'type': 'no_change',
                    'content': '',
                    'size': 0,
                    'new_text_size': len(new_text),
                    'diff_size': 0,
                    'ratio': 0.0
                }
            filtered_lines = []
            filtered_indices = []
            for idx in sorted(changed_indices):
                line = diff_lines[idx]
                if not line.startswith('? '):
                    filtered_lines.append(line)
                    filtered_indices.append(idx)
            result_lines = []
            for i, (idx, line) in enumerate(zip(filtered_indices, filtered_lines)):
                if i > 0:
                    prev_idx = filtered_indices[i - 1]
                    if idx - prev_idx > 2:
                        result_lines.append('...\n')
                result_lines.append(line.rstrip('\n') + '\n')
            diff_content = ''.join(result_lines).rstrip('\n')
        else:
            diff_lines = list(difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile='before',
                tofile='after',
                lineterm='',
                n=context_lines
            ))
            if not diff_lines:
                return {
                    'type': 'no_change',
                    'content': '',
                    'size': 0,
                    'new_text_size': len(new_text),
                    'diff_size': 0,
                    'ratio': 0.0
                }
            diff_content = '\n'.join(diff_lines)
        diff_size = len(diff_content)
        new_size = len(new_text)
        ratio = diff_size / new_size if new_size > 0 else 0
        if ratio > threshold_ratio:
            return {
                'type': 'full',
                'content': new_text,
                'size': new_size,
                'new_text_size': new_size,
                'diff_size': diff_size,
                'ratio': ratio
            }
        else:
            return {
                'type': 'diff',
                'content': diff_content,
                'size': diff_size,
                'new_text_size': new_size,
                'diff_size': diff_size,
                'ratio': ratio
            }
