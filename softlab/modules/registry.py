import importlib
import pkgutil
from softlab.modules.base import AnalysisModule


class ModuleRegistry:
    def __init__(self):
        self._modules: dict[str, AnalysisModule] = {}
        self._autodiscover()

    def _autodiscover(self):
        """
        Escanea el paquete softlab.modules buscando subpaquetes
        que contengan una clase Module(AnalysisModule).
        Agregar un módulo nuevo = crear carpeta + implementar la clase.
        """
        import softlab.modules as modules_pkg

        for _, name, ispkg in pkgutil.iter_modules(modules_pkg.__path__):
            if not ispkg or name in ("base", "registry"):
                continue
            try:
                mod = importlib.import_module(f"softlab.modules.{name}.module")
                cls = getattr(mod, "Module", None)
                if cls and issubclass(cls, AnalysisModule) and cls is not AnalysisModule:
                    instance = cls()
                    self._modules[instance.module_id] = instance
            except Exception as e:
                print(f"[Registry] No se pudo cargar módulo '{name}': {e}")

    def get(self, module_id: str) -> AnalysisModule | None:
        return self._modules.get(module_id)

    def all(self) -> list[AnalysisModule]:
        return list(self._modules.values())

    def available_ids(self) -> list[str]:
        return list(self._modules.keys())


# Instancia global — se inicializa una vez al arrancar
registry = ModuleRegistry()
