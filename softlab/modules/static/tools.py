import subprocess
import json
from softlab.core.graph_builder import ProjectGraph


def run_radon_cc(root_path: str) -> list[dict]:
    """Complejidad ciclomática con radon."""
    try:
        result = subprocess.run(
            ["python3", "-m", "radon", "cc", root_path, "-j", "-s"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        data = json.loads(result.stdout)
        findings = []
        for filepath, functions in data.items():
            for fn in functions:
                findings.append({
                    "file":       filepath,
                    "name":       fn.get("name", "unknown"),
                    "complexity": fn.get("complexity", 0),
                    "line":       fn.get("lineno", 1),
                    "rank":       fn.get("rank", "A"),
                })
        return findings
    except Exception:
        return []


def run_radon_mi(root_path: str) -> list[dict]:
    """Maintainability Index con radon."""
    try:
        result = subprocess.run(
            ["python3", "-m", "radon", "mi", root_path, "-j"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        data = json.loads(result.stdout)
        return [
            {"file": fp, "mi": info.get("mi", 100), "rank": info.get("rank", "A")}
            for fp, info in data.items()
        ]
    except Exception:
        return []
