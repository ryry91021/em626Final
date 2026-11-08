import json
from pathlib import Path

from ollama import chat
from pydantic import BaseModel, model_validator


class Component(BaseModel):
    id: str
    name: str
    type: str
    description: str
    subsystem: str | None = None


class Dependency(BaseModel):
    source: str
    target: str
    interface: str | None = None


class SystemGraph(BaseModel):
    nodes: list[Component]
    edges: list[Dependency]

    @model_validator(mode="after")
    def validate_graph(self):
        ids = [node.id for node in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate component IDs")

        valid_ids = set(ids)

        for edge in self.edges:
            if edge.source not in valid_ids:
                raise ValueError(f"Unknown source: {edge.source}")
            if edge.target not in valid_ids:
                raise ValueError(f"Unknown target: {edge.target}")

        return self


SYSTEM_PROMPT = """
You are a systems engineering information extractor.

Extract:
- System components
- Component types and descriptions
- Subsystem membership
- Directed dependencies
- Interfaces associated with dependencies

Rules:
1. Only extract information supported by the input.
2. Do not invent additional components or dependencies.
3. Use unique, consistent component IDs.
4. An edge A -> B means A depends on B.
5. Do not confuse response traffic with dependencies.
6. Return JSON matching the supplied schema.
"""


def extract_system(description: str) -> SystemGraph:
    response = chat(
        model="qwen3.5:4b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description}
        ],
        format=SystemGraph.model_json_schema(),
        options={"temperature": 0}
    )

    return SystemGraph.model_validate_json(
        response.message.content
    )


if __name__ == "__main__":
    description = Path(
        "data/system_description.txt"
    ).read_text(encoding="utf-8")

    graph = extract_system(description)

    output = Path("outputs/extracted_system.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(graph.model_dump(), indent=2),
        encoding="utf-8"
    )

    print(f"Components: {len(graph.nodes)}")
    print(f"Dependencies: {len(graph.edges)}")
    print(f"Saved to: {output}")