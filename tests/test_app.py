import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from main import DEFAULT_EXTENSION, ExtensionWatcher, calculate


class ExtensionTests(unittest.TestCase):
    def test_default_discount(self):
        self.assertEqual(calculate(DEFAULT_EXTENSION.read_text(encoding="utf-8")).discount, 40000)

    def test_errors_preserve_result_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.lua"
            original = DEFAULT_EXTENSION.read_text(encoding="utf-8")
            path.write_text(original, encoding="utf-8")
            watcher = ExtensionWatcher(path)
            self.assertTrue(watcher.refresh())
            for invalid in (
                "function calculate(",
                "function calculate(cart) error('broken') end",
                "function calculate(cart) return {discount=-1, message='bad'} end",
                "function calculate(cart) return {discount=400001, message='bad'} end",
                "function calculate(cart) return {discount=true, message='bad'} end",
                "function calculate(cart) return 42 end",
                "x = 1",
            ):
                with self.subTest(source=invalid), contextlib.redirect_stdout(io.StringIO()):
                    path.write_text(invalid, encoding="utf-8")
                    self.assertFalse(watcher.refresh())
                    self.assertEqual(watcher.receipt.discount, 40000)
            path.unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(watcher.refresh())
            path.write_text(original.replace("= 10", "= 20"), encoding="utf-8")
            self.assertTrue(watcher.refresh())
            self.assertEqual(watcher.receipt.discount, 80000)
            self.assertFalse(watcher.refresh())

    def test_hot_reload_in_same_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.lua"
            output = Path(directory) / "output.txt"
            original = DEFAULT_EXTENSION.read_text(encoding="utf-8")
            path.write_text(original, encoding="utf-8")
            with output.open("w", encoding="utf-8") as stream:
                process = subprocess.Popen(
                    [sys.executable, "-X", "utf8", "-u", str(DEFAULT_EXTENSION.parent.parent / "main.py"), "--extension", str(path)],
                    stdout=stream, stderr=subprocess.STDOUT,
                )
                try:
                    def wait_for(text):
                        deadline = time.monotonic() + 10
                        while time.monotonic() < deadline:
                            if text in output.read_text(encoding="utf-8"):
                                return
                            if process.poll() is not None:
                                self.fail(output.read_text(encoding="utf-8"))
                            time.sleep(0.1)
                        self.fail(f"Не дождались {text}: {output.read_text(encoding='utf-8')}")

                    wait_for("3600.00")
                    path.write_text("function calculate(cart) error('test failure') end", encoding="utf-8")
                    wait_for("Ошибка расширения")
                    path.write_text(original.replace("= 10", "= 20"), encoding="utf-8")
                    wait_for("3200.00")
                    self.assertIsNone(process.poll())
                finally:
                    process.terminate()
                    process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
