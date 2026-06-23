from __future__ import annotations

from agentic_web_poisoning_lab.schema import Condition


CONDITIONS: dict[str, Condition] = {
    "A0_DIRECT": Condition(
        id="A0_DIRECT",
        name="Direct answer",
        browse=False,
        source_ranking=False,
        prompt_shields=False,
        trust_filter=False,
        citation_validation=False,
        abstain_on_conflict=False,
    ),
    "A1_AGENT_BASELINE": Condition(
        id="A1_AGENT_BASELINE",
        name="Agent baseline",
        browse=True,
        source_ranking=False,
        prompt_shields=False,
        trust_filter=False,
        citation_validation=False,
        abstain_on_conflict=False,
    ),
    "A2_SOURCE_RANKING": Condition(
        id="A2_SOURCE_RANKING",
        name="Source ranking",
        browse=True,
        source_ranking=True,
        prompt_shields=False,
        trust_filter=False,
        citation_validation=True,
        abstain_on_conflict=True,
    ),
    "A3_PROMPT_SHIELDS": Condition(
        id="A3_PROMPT_SHIELDS",
        name="Prompt Shields",
        browse=True,
        source_ranking=False,
        prompt_shields=True,
        trust_filter=False,
        citation_validation=True,
        abstain_on_conflict=False,
    ),
    "A4_FULL_DEFENSE": Condition(
        id="A4_FULL_DEFENSE",
        name="Full defense",
        browse=True,
        source_ranking=True,
        prompt_shields=True,
        trust_filter=True,
        citation_validation=True,
        abstain_on_conflict=True,
    ),
    "A5_STRICT_ABSTENTION": Condition(
        id="A5_STRICT_ABSTENTION",
        name="Strict abstention",
        browse=True,
        source_ranking=True,
        prompt_shields=True,
        trust_filter=True,
        citation_validation=True,
        abstain_on_conflict=True,
        strict_abstention=True,
    ),
}


DEFAULT_CONDITIONS = [
    "A0_DIRECT",
    "A1_AGENT_BASELINE",
    "A2_SOURCE_RANKING",
    "A3_PROMPT_SHIELDS",
    "A4_FULL_DEFENSE",
]
