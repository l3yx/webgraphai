import subprocess
import uuid
import re
from pathlib import Path


class Playwright:
    def __init__(self, headed: bool = True, browser: str = "chrome"):
        self._session_name = f"session_{uuid.uuid4().hex[:8]}"
        self._headed = headed
        self._browser = browser

    def __enter__(self):
        self.run("tab-list")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def _expand_file_refs(self, text: str) -> str:
        pattern = r'- \[Snapshot\]\(([^)]+)\)'

        def replace_ref(match):
            file_path = match.group(1)
            path = Path(file_path)
            if path.exists():
                try:
                    return path.read_text()
                except Exception:
                    pass
            return match.group(0)
        return re.sub(pattern, replace_ref, text)

    def read_file(self, file_path: str, line: int | None = None) -> str:
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

    def run(self, *args: str) -> str:
        cmd = ["playwright-cli", f"--session={self._session_name}"]
        if self._headed:
            cmd.append("--headed")
        if self._browser:
            cmd.extend(["--browser", self._browser])
        cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        stdout = self._expand_file_refs(result.stdout)
        return stdout

    def close(self):
        try:
            self.run("session-stop", self._session_name)
            self.run("session-delete", self._session_name)
        except Exception:
            pass


if __name__ == "__main__":
    import time

    with Playwright(headed=True) as pw:
        print(pw.read_file(".playwright-cli/console-2026-02-05T12-28-46-774Z.log", 1))

        print(f"Session: {pw._session_name}")

        output = pw.run("open", "https://www.example.com")
        print(output)
        time.sleep(1)
        print("\n....\n")

        output = pw.run("tab-new", "https://www.baidu.com")
        print(output)
        time.sleep(1)
        print("\n....\n")

        output = pw.run("tab-list")
        print(output)
        time.sleep(1)
        print("\n....\n")

        output = pw.run("tab-select", "0")
        print(output)
        time.sleep(1)
        print("\n....\n")

        output = pw.run("screenshot")
        print(output)
