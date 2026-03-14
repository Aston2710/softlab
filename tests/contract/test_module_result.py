from softlab.modules.base import (
    CodeLocation, Issue, ModuleResult, Severity,
)


def make_valid_result() -> ModuleResult:
    return ModuleResult(
        module_id="test_module",
        version="1.0.0",
        language="python",
        status="success",
        score=0.85,
        issues=[
            Issue(
                id="TEST-01-a1b2",
                rule_id="TEST-01",
                severity=Severity.WARNING,
                title="Issue de prueba",
                description="Descripción del problema",
                suggestion="Cómo resolverlo",
                location=CodeLocation(file_path="main.py", line_start=10),
            )
        ],
        metrics={"total_files": 1},
        duration_ms=150,
    )


def test_module_result_schema():
    result = make_valid_result()
    assert isinstance(result, ModuleResult)
    assert result.status in ("success", "partial", "failed")
    assert 0.0 <= result.score <= 1.0
    assert isinstance(result.issues, list)
    assert isinstance(result.duration_ms, int)


def test_issue_schema():
    result = make_valid_result()
    for issue in result.issues:
        assert isinstance(issue.severity, Severity)
        assert len(issue.title) <= 80
        assert issue.description != ""
        assert issue.suggestion != ""
        assert issue.location.file_path != ""
        assert issue.location.line_start > 0


def test_severity_values():
    values = {s.value for s in Severity}
    assert values == {"critical", "warning", "suggestion", "excellent"}


def test_score_boundaries():
    result = make_valid_result()
    result.score = 0.0
    assert result.score == 0.0
    result.score = 1.0
    assert result.score == 1.0
