# ARCHIVO INMUTABLE — ver ADR-01 y ADR-06
# Cambios aquí requieren versioning y actualización de todos los módulos
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from softlab.core.graph_builder import ProjectGraph
    from softlab.providers.llm.base import LLMProvider


class Severity(Enum):
    CRITICAL   = "critical"
    WARNING    = "warning"
    SUGGESTION = "suggestion"
    EXCELLENT  = "excellent"


@dataclass
class CodeLocation:
    file_path:  str
    line_start: int
    line_end:   Optional[int] = None
    column:     Optional[int] = None


@dataclass
class Issue:
    id:          str           # formato: '{MODULE_ID}-{RULE}-{hash4}'
    rule_id:     str           # e.g. 'EST-01', 'SEC-03'
    severity:    Severity
    title:       str           # max 80 chars
    description: str           # por qué es un problema
    suggestion:  str           # cómo resolverlo
    location:    CodeLocation
    snippet:     Optional[str]        = None
    references:  list[str]            = field(default_factory=list)
    metadata:    dict                 = field(default_factory=dict)


@dataclass
class ModuleResult:
    module_id:   str
    version:     str
    language:    str
    status:      str           # "success" | "partial" | "failed"
    score:       float         # 0.0 — 1.0
    issues:      list[Issue]
    metrics:     dict
    duration_ms: int
    error:       Optional[str] = None


class AnalysisModule(ABC):
    module_id:           str
    version:             str
    supported_languages: list[str]

    @abstractmethod
    async def analyze(
        self,
        graph: "ProjectGraph",
        config: dict,
        llm: "LLMProvider",
    ) -> ModuleResult:
        """
        Ejecuta el análisis sobre el ProjectGraph completo.
        NUNCA lanza excepciones al Orchestrator.
        En caso de error interno, retorna ModuleResult con status='failed'.
        """
        ...

    def health_check(self) -> bool:
        """Verifica que las herramientas externas del módulo están disponibles."""
        return True
