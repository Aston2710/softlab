import time
import uuid
import os
from softlab.modules.base import (
    AnalysisModule, ModuleResult, Issue, Severity, CodeLocation,
)
from softlab.core.graph_builder import ProjectGraph
from softlab.providers.llm.base import LLMProvider
from softlab.modules.static.tools import run_radon_cc, run_radon_mi

PENALTIES = {
    Severity.CRITICAL:   0.15,
    Severity.WARNING:    0.05,
    Severity.SUGGESTION: 0.01,
    Severity.EXCELLENT: -0.02,
}

CC_WARNING  = 10
CC_CRITICAL = 20
MI_WARNING  = 20
MI_CRITICAL = 10


class Module(AnalysisModule):
    module_id            = "static"
    version              = "1.0.0"
    supported_languages  = ["python"]

    async def analyze(
        self,
        graph: ProjectGraph,
        config: dict,
        llm: LLMProvider,
    ) -> ModuleResult:
        start  = time.time()
        issues: list[Issue] = []

        try:
            cc_results = run_radon_cc(graph.root_path)
            for r in cc_results:
                complexity = r["complexity"]
                if complexity > CC_CRITICAL:
                    severity = Severity.CRITICAL
                    title    = f"Complejidad ciclomática crítica: {r['name']} (CC={complexity})"
                    desc     = (f"La función '{r['name']}' tiene complejidad ciclomática {complexity}, "
                                f"muy por encima del umbral crítico ({CC_CRITICAL}+). "
                                "Esto indica demasiados caminos de ejecución, haciendo el código "
                                "difícil de entender, testear y mantener.")
                    sug      = ("Divide esta función en funciones más pequeñas con responsabilidad única. "
                                "Extrae bloques condicionales complejos a funciones auxiliares.")
                elif complexity > CC_WARNING:
                    severity = Severity.WARNING
                    title    = f"Complejidad ciclomática alta: {r['name']} (CC={complexity})"
                    desc     = (f"La función '{r['name']}' tiene complejidad ciclomática {complexity} "
                                f"(umbral recomendado: {CC_WARNING}). Considera simplificarla.")
                else:
                    continue

                rel_path = os.path.relpath(r["file"], graph.root_path)
                issues.append(Issue(
                    id          = f"static-cc-{uuid.uuid4().hex[:4]}",
                    rule_id     = "EST-01",
                    severity    = severity,
                    title       = title,
                    description = desc,
                    suggestion  = sug,
                    location    = CodeLocation(file_path=rel_path, line_start=r["line"]),
                    metadata    = {"complexity": complexity, "rank": r["rank"]},
                    references  = ["https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity"],
                ))

            mi_results = run_radon_mi(graph.root_path)
            for r in mi_results:
                mi       = r["mi"]
                rel_path = os.path.relpath(r["file"], graph.root_path) if os.path.isabs(r["file"]) else r["file"]
                fname    = os.path.basename(rel_path)

                if mi < MI_CRITICAL:
                    severity = Severity.CRITICAL
                    title    = f"MI crítico: {fname} (MI={mi:.1f})"
                    desc     = (f"El archivo tiene un Maintainability Index de {mi:.1f}/100. "
                                "Un MI bajo indica que el código es muy difícil de mantener.")
                    sug      = "Considera refactorizar este archivo: reduce su tamaño, simplifica funciones y elimina código duplicado."
                elif mi < MI_WARNING:
                    severity = Severity.WARNING
                    title    = f"MI bajo: {fname} (MI={mi:.1f})"
                    desc     = f"MI={mi:.1f}/100. Por debajo del umbral recomendado ({MI_WARNING})."
                    sug      = "Revisa las funciones más complejas del archivo y simplifica donde sea posible."
                else:
                    issues.append(Issue(
                        id          = f"static-mi-{uuid.uuid4().hex[:4]}",
                        rule_id     = "EST-MI",
                        severity    = Severity.EXCELLENT,
                        title       = f"Buen MI: {fname} (MI={mi:.1f})",
                        description = "El archivo mantiene un buen índice de mantenibilidad.",
                        suggestion  = "Continúa con las buenas prácticas actuales.",
                        location    = CodeLocation(file_path=rel_path, line_start=1),
                    ))
                    continue

                issues.append(Issue(
                    id          = f"static-mi-{uuid.uuid4().hex[:4]}",
                    rule_id     = "EST-MI",
                    severity    = severity,
                    title       = title,
                    description = desc,
                    suggestion  = sug,
                    location    = CodeLocation(file_path=rel_path, line_start=1),
                    metadata    = {"mi": mi, "rank": r["rank"]},
                ))

            score  = self._calculate_score(issues)
            status = "success"
            error  = None

        except Exception as e:
            score  = 0.0
            status = "failed"
            error  = str(e)
            issues = []

        metrics = {
            "total_functions_analyzed": len(run_radon_cc(graph.root_path)) if status == "success" else 0,
            "total_files_analyzed":     len(graph.files),
            "issues_critical":          sum(1 for i in issues if i.severity == Severity.CRITICAL),
            "issues_warning":           sum(1 for i in issues if i.severity == Severity.WARNING),
        }

        return ModuleResult(
            module_id   = self.module_id,
            version     = self.version,
            language    = graph.language,
            status      = status,
            score       = score,
            issues      = issues,
            metrics     = metrics,
            duration_ms = int((time.time() - start) * 1000),
            error       = error,
        )

    def _calculate_score(self, issues: list[Issue]) -> float:
        score = 1.0
        for issue in issues:
            score -= PENALTIES[issue.severity]
        return max(0.0, min(1.0, score))

    def health_check(self) -> bool:
        try:
            import subprocess
            r = subprocess.run(
                ["python3", "-m", "radon", "--version"],
                capture_output=True, timeout=5
            )
            return r.returncode == 0
        except Exception:
            return False
