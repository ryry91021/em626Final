
from pathlib import Path

import networkx as nx

from src.llm_extractor import SystemGraph


def build_graph(system: SystemGraph) -> nx.DiGraph:
    """
    Convert an extracted system into a directed dependency graph.

    Nodes represent components.
    Edges represent dependencies: A -> B means A depends on B.
    """

    graph = nx.DiGraph()

    # Add system components as nodes
    for component in system.nodes:
        attributes = {
            "name": component.name,
            "type": component.type,
            "description": component.description,
        }

        if component.subsystem is not None:
            attributes["subsystem"] = component.subsystem

        graph.add_node(component.id, **attributes)

    # Add component dependencies as directed edges
    for dependency in system.edges:

        if dependency.source == dependency.target:
            raise ValueError(
                f"Self-dependency: {dependency.source}"
            )

        if graph.has_edge(dependency.source, dependency.target):
            raise ValueError(
                f"Duplicate dependency: "
                f"{dependency.source} -> {dependency.target}"
            )

        attributes = {"type": "depends_on"}

        if dependency.interface is not None:
            attributes["interface"] = dependency.interface

        graph.add_edge(
            dependency.source,
            dependency.target,
            **attributes
        )

    return graph


if __name__ == "__main__":

    input_path = Path("outputs/extracted_system.json")

    system = SystemGraph.model_validate_json(
        input_path.read_text(encoding="utf-8")
    )

    graph = build_graph(system)

    output_path = Path("outputs/system_graph.gexf")

    nx.write_gexf(graph, output_path)

    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    print("\nComponents:")
    for node_id, attributes in graph.nodes(data=True):
        print(f"  {node_id}: {attributes['name']}")

    print("\nDependencies:")
    for source, target in graph.edges():
        print(f"  {source} -> {target}")

    print(f"\nGraph saved to: {output_path}")
