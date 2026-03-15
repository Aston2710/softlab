import pytest
import os
from softlab.core.graph_builder import GraphBuilder
from softlab.modules.static.module import Module
from softlab.modules.base import ModuleResult, Severity


FIXTURE_PATH = "/mnt/c/Users/redon/Desktop/projects/SoftLab/tests/fixtures/sample_projects/python_simple"


class MockLLM:
    async def complete(self, prompt, system="", max_tokens=1000, temperature=0.1):
        return ""
    async def complete_json(self, prompt, schema, system=""):
        return {}


@pytest.fixture
def graph():
    return GraphBuilder().build("test", FIXTURE_PATH)


@pytest.fixture
def module():
    return Module()


def test_module_id(module):
    assert module.module_id == "static"
    assert module.version == "1.0.0"
    assert "python" in module.supported_languages


def test_health_check(module):
    assert module.health_check() is True


@pytest.mark.asyncio
async def test_analyze_returns_module_result(graph, module):
    result = await module.analyze(graph, config={}, llm=MockLLM())
    assert isinstance(result, ModuleResult)
    assert result.status in ("success", "partial", "failed")
    assert 0.0 <= result.score <= 1.0
    assert result.module_id == "static"
    assert isinstance(result.issues, list)
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_analyze_never_raises(graph, module):
    """El módulo nunca debe propagar excepciones — ADR-01."""
    result = await module.analyze(graph, config={}, llm=MockLLM())
    assert result is not None


@pytest.mark.asyncio
async def test_issues_respect_schema(graph, module):
    result = await module.analyze(graph, config={}, llm=MockLLM())
    for issue in result.issues:
        assert isinstance(issue.severity, Severity)
        assert len(issue.title) <= 80
        assert issue.description != ""
        assert issue.suggestion != ""
        assert issue.location.file_path != ""
        assert issue.location.line_start > 0
