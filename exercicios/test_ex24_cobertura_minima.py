"""Exercício 24: cobertura mínima no task test."""

import re
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"


def test_task_test_exige_cobertura_minima():
    config = tomllib.loads(PYPROJECT.read_text("utf-8"))
    comando = config["tool"]["taskipy"]["tasks"]["test"]

    assert re.search(r"--cov-fail-under[= ]\d+", comando)
