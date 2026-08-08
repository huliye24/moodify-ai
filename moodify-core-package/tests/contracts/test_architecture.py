import ast
from pathlib import Path


def test_contracts_do_not_import_high_level_subsystems():
    package = Path(__file__).parents[2] / "src" / "moodify" / "contracts"
    prohibited = (
        "moodify_runtime",
        "apps.android",
        "moodify.learning",
        "moodify.auditory",
        "moodify.app",
    )
    imports: list[tuple[Path, str]] = []
    for source in package.rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend((source, alias.name) for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append((source, node.module))

    violations = [
        f"{source.name}: {name}"
        for source, name in imports
        if name.startswith(prohibited)
    ]
    assert not violations, "prohibited contract imports: " + ", ".join(violations)
