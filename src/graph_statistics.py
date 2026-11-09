
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


def analyze_graph(graph: nx.DiGraph) -> dict:
    degree_counts = Counter(
        degree for _, degree in graph.degree()
    )

    stats = {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "weakly_connected_components":
            nx.number_weakly_connected_components(graph),
        "isolated_nodes": list(nx.isolates(graph)),
        "degree_distribution": dict(sorted(degree_counts.items())),
        "components": [
            {
                "id": node,
                "name": graph.nodes[node].get("name", node),
                "in_degree": graph.in_degree(node),
                "out_degree": graph.out_degree(node),
                "total_degree": graph.degree(node),
            }
            for node in graph.nodes()
        ],
    }

    return stats


def visualize_graph(graph: nx.DiGraph, output: Path):
    plt.figure(figsize=(11, 7))

    positions = nx.spring_layout(graph, seed=42)

    labels = {
        node: data.get("name", node)
        for node, data in graph.nodes(data=True)
    }

    nx.draw_networkx(
        graph,
        pos=positions,
        labels=labels,
        node_size=3500,
        font_size=10,
        arrows=True,
        arrowsize=20,
        node_color="lightblue",
        edge_color="gray",
    )

    plt.title("System Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close()


def visualize_degree_distribution(stats: dict, output: Path):
    distribution = stats["degree_distribution"]

    degrees = list(distribution.keys())
    counts = list(distribution.values())

    plt.figure(figsize=(8, 5))
    plt.bar(degrees, counts)
    plt.xticks(degrees)
    plt.xlabel("Node Degree")
    plt.ylabel("Number of Components")
    plt.title("Degree Distribution")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


if __name__ == "__main__":
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    graph = nx.read_gexf(output_dir / "system_graph.gexf")

    stats = analyze_graph(graph)

    (output_dir / "graph_statistics.json").write_text(
        json.dumps(stats, indent=2),
        encoding="utf-8",
    )

    visualize_graph(graph, output_dir / "system_graph.png")
    visualize_degree_distribution(
        stats,
        output_dir / "degree_distribution.png",
    )

    print(json.dumps(stats, indent=2))
    print("Graph visualizations saved.")
