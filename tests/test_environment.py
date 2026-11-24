"""Environment smoke test: imports, .env key presence, AniList connectivity.

Run with:  pytest tests/test_environment.py -v -s
Never prints secret values -- only "found" / "missing".
"""

import importlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

# pip package name -> import name
PACKAGES = {
    "requests": "requests",
    "pandas": "pandas",
    "numpy": "numpy",
    "python-dotenv": "dotenv",
    "rank-bm25": "rank_bm25",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
    "anthropic": "anthropic",
    "streamlit": "streamlit",
    "pytest": "pytest",
}


@pytest.mark.parametrize("pip_name,module_name", PACKAGES.items())
def test_import(pip_name, module_name):
    importlib.import_module(module_name)


def _api_key_status() -> str:
    """Return "found" or "missing". The key value never leaves this function."""
    from dotenv import dotenv_values

    if not ENV_PATH.is_file():
        return "missing"
    value = dotenv_values(ENV_PATH).get("ANTHROPIC_API_KEY") or ""
    value = value.strip()
    return "found" if value and value != "your_key_here" else "missing"


def test_anthropic_api_key_in_dotenv():
    status = _api_key_status()
    print(f"\nANTHROPIC_API_KEY: {status}")
    if status == "missing":
        pytest.skip("ANTHROPIC_API_KEY: missing (create .env from .env.example)")


def test_anilist_connectivity():
    import requests

    query = "query { Media(id: 1) { id title { romaji } } }"
    resp = requests.post(
        "https://graphql.anilist.co",
        json={"query": query},
        headers={"Accept": "application/json"},
        timeout=15,
    )
    assert resp.status_code == 200, f"AniList returned HTTP {resp.status_code}"
    title = resp.json()["data"]["Media"]["title"]["romaji"]
    assert title
    print(f"\nAniList OK: fetched '{title}'")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
