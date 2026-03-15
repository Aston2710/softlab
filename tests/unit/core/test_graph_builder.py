import os
import pytest
from softlab.core.graph_builder import GraphBuilder, ProjectGraph, FileNode


FIXTURE_PATH = "/mnt/c/Users/redon/Desktop/projects/SoftLab/tests/fixtures/sample_projects/python_simple"


@pytest.fixture
def graph() -> ProjectGraph:
    builder = GraphBuilder()
    return builder.build("test-project", FIXTURE_PATH)


def test_graph_builds_successfully(graph):
    assert isinstance(graph, ProjectGraph)
    assert graph.project_id == "test-project"
    assert graph.language == "python"


def test_graph_finds_all_files(graph):
    assert len(graph.files) == 2
    paths = set(graph.files.keys())
    assert "main.py" in paths
    assert "utils.py" in paths


def test_file_nodes_have_ast(graph):
    for path, node in graph.files.items():
        assert isinstance(node, FileNode)
        assert node.ast is not None, f"AST vacío en {path}"
        assert node.content != ""
        assert node.size_loc > 0


def test_imports_extracted(graph):
    main_node = graph.files["main.py"]
    assert any("utils" in imp for imp in main_node.imports)


def test_edges_built(graph):
    assert len(graph.edges) > 0
    sources = {e.source for e in graph.edges}
    assert "main.py" in sources


def test_get_dependencies(graph):
    deps = graph.get_dependencies("main.py")
    assert any(f.path == "utils.py" for f in deps)


def test_detect_cycles_none(graph):
    cycles = graph.detect_cycles()
    assert cycles == []


def test_get_all_functions(graph):
    functions = graph.get_all_functions()
    names = {f["name"] for f in functions}
    assert "greet" in names
    assert "add" in names
    assert "main" in names


def test_get_subgraph(graph):
    sub = graph.get_subgraph("main.py", depth=1)
    assert "main.py" in sub.files
    assert "utils.py" in sub.files
