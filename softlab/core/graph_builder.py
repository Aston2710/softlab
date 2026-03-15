from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FileNode:
    path:      str
    language:  str
    content:   str
    ast:       Any
    imports:   list[str] = field(default_factory=list)
    exports:   list[str] = field(default_factory=list)
    size_loc:  int       = 0


@dataclass
class DependencyEdge:
    source:    str
    target:    str
    edge_type: str


@dataclass
class ProjectGraph:
    project_id: str
    root_path:  str
    language:   str
    files:      dict[str, FileNode]  = field(default_factory=dict)
    edges:      list[DependencyEdge] = field(default_factory=list)
    metadata:   dict                 = field(default_factory=dict)

    def get_dependencies(self, path: str) -> list[FileNode]:
        targets = {e.target for e in self.edges if e.source == path}
        return [self.files[t] for t in targets if t in self.files]

    def get_dependents(self, path: str) -> list[FileNode]:
        sources = {e.source for e in self.edges if e.target == path}
        return [self.files[s] for s in sources if s in self.files]

    def get_subgraph(self, path: str, depth: int = 2) -> ProjectGraph:
        """Subgrafo centrado en path hasta depth niveles de dependencias."""
        visited: set[str] = {path}
        frontier: set[str] = {path}

        for _ in range(depth):
            next_frontier: set[str] = set()
            for p in frontier:
                for e in self.edges:
                    if e.source == p and e.target not in visited:
                        next_frontier.add(e.target)
            visited.update(next_frontier)
            frontier = next_frontier
            if not frontier:
                break

        sub_files = {p: self.files[p] for p in visited if p in self.files}
        sub_edges = [
            e for e in self.edges
            if e.source in visited and e.target in visited
        ]
        return ProjectGraph(
            project_id=self.project_id,
            root_path=self.root_path,
            language=self.language,
            files=sub_files,
            edges=sub_edges,
            metadata=self.metadata,
        )

    def detect_cycles(self) -> list[list[str]]:
        visited:   set[str]        = set()
        rec_stack: set[str]        = set()
        cycles:    list[list[str]] = []

        adj: dict[str, list[str]] = {p: [] for p in self.files}
        for e in self.edges:
            if e.source in adj:
                adj[e.source].append(e.target)

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])
            path.pop()
            rec_stack.discard(node)

        for node in list(self.files.keys()):
            if node not in visited:
                dfs(node, [])
        return cycles

    def get_all_functions(self) -> list[dict]:
        functions = []
        for path, node in self.files.items():
            functions.extend(_extract_functions(node))
        return functions


def _extract_functions(file_node: FileNode) -> list[dict]:
    results = []
    if file_node.ast is None:
        return results

    def walk(node: Any) -> None:
        if node.type in (
            "function_definition", "method_definition",
            "function_declaration", "method_declaration",
        ):
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode() if name_node else "anonymous"
            results.append({
                "name": name,
                "file": file_node.path,
                "line": node.start_point[0] + 1,
                "node": node,
            })
        for child in node.children:
            walk(child)

    walk(file_node.ast)
    return results


class GraphBuilder:
    LANGUAGE_MAP = {
        ".py":   "python",
        ".js":   "javascript",
        ".ts":   "javascript",
        ".jsx":  "javascript",
        ".tsx":  "javascript",
        ".java": "java",
    }

    def __init__(self) -> None:
        self._parsers: dict[str, Any] = {}
        self._load_parsers()

    def _load_parsers(self) -> None:
        from tree_sitter import Language, Parser
        import tree_sitter_python     as tspython
        import tree_sitter_javascript as tsjavascript
        import tree_sitter_java       as tsjava

        self._parsers["python"]     = Parser(Language(tspython.language()))
        self._parsers["javascript"] = Parser(Language(tsjavascript.language()))
        self._parsers["java"]       = Parser(Language(tsjava.language()))

    def build(self, project_id: str, root_path: str) -> ProjectGraph:
        import os

        lang_counts: dict[str, int] = {}
        for dirpath, _, filenames in os.walk(root_path):
            for fname in filenames:
                ext  = os.path.splitext(fname)[1]
                lang = self.LANGUAGE_MAP.get(ext)
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

        if not lang_counts:
            raise ValueError(f"No se encontraron archivos soportados en {root_path}")

        dominant_lang = max(lang_counts, key=lambda k: lang_counts[k])
        graph = ProjectGraph(
            project_id=project_id,
            root_path=root_path,
            language=dominant_lang,
            metadata={"language_counts": lang_counts},
        )

        for dirpath, _, filenames in os.walk(root_path):
            for fname in filenames:
                ext  = os.path.splitext(fname)[1]
                lang = self.LANGUAGE_MAP.get(ext)
                if not lang:
                    continue
                full_path = os.path.join(dirpath, fname)
                rel_path  = os.path.relpath(full_path, root_path)
                file_node = self._parse_file(full_path, rel_path, lang)
                if file_node:
                    graph.files[rel_path] = file_node

        self._build_edges(graph)
        return graph

    def _parse_file(
        self, full_path: str, rel_path: str, lang: str
    ) -> Optional[FileNode]:
        try:
            with open(full_path, "rb") as f:
                content_bytes = f.read()
            content = content_bytes.decode("utf-8", errors="replace")
            parser  = self._parsers.get(lang)
            if not parser:
                return None
            tree    = parser.parse(content_bytes)
            imports = self._extract_imports(tree.root_node, lang)
            loc     = content.count("\n")
            return FileNode(
                path=rel_path, language=lang, content=content,
                ast=tree.root_node, imports=imports, size_loc=loc,
            )
        except Exception:
            return None

    def _extract_imports(self, root_node: Any, lang: str) -> list[str]:
        imports: list[str] = []
        if lang == "python":
            for node in root_node.children:
                if node.type in ("import_statement", "import_from_statement"):
                    imports.append(node.text.decode(errors="replace"))
        elif lang == "javascript":
            for node in root_node.children:
                if node.type == "import_statement":
                    imports.append(node.text.decode(errors="replace"))
        elif lang == "java":
            for node in root_node.children:
                if node.type == "import_declaration":
                    imports.append(node.text.decode(errors="replace"))
        return imports

    def _build_edges(self, graph: ProjectGraph) -> None:
        for src_path, file_node in graph.files.items():
            for imp in file_node.imports:
                target = self._resolve_import(imp, src_path, graph)
                if target:
                    graph.edges.append(DependencyEdge(
                        source=src_path, target=target, edge_type="import"
                    ))

    def _resolve_import(
        self, imp: str, src_path: str, graph: ProjectGraph
    ) -> Optional[str]:
        import os
        src_dir = os.path.dirname(src_path)

        if imp.startswith("from "):
            parts = imp.split()
            if len(parts) >= 2:
                module = parts[1].lstrip(".").replace(".", os.sep)
                candidates = [
                    f"{module}.py",
                    os.path.join(module, "__init__.py"),
                    os.path.join(src_dir, f"{module}.py"),
                ]
                for c in candidates:
                    norm = os.path.normpath(c)
                    if norm in graph.files:
                        return norm
        return None
