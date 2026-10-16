import os
import sys
import subprocess

def test_all_tests_pass():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--ignore", "tests/test_integration.py"],
        capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..')
    )
    assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"