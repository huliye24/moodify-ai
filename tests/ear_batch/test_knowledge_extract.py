import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "ops" / "ear_batch" / "knowledge_extract.py"
SPEC = importlib.util.spec_from_file_location("knowledge_extract", MODULE_PATH)
knowledge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(knowledge)


def test_claim_type_does_not_mark_proposal_verified():
    assert knowledge.claim_type("The system should preserve time-local evidence for later review.") == "proposal_or_requirement"


def test_sections_and_sentences():
    text = "# Title\n\nA sufficiently long statement describes the auditory representation in a reproducible way."
    parsed = knowledge.sections(text)
    assert parsed[0][0] == "Title"
    assert list(knowledge.sentences(parsed[0][1]))
