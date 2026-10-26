import re
from functools import lru_cache
from pathlib import Path

from .renderer import context_value_to_bool


MAPPING_PATH = Path(__file__).with_name("protocol_placeholder_aliases.md")

PLACEHOLDER_LINE_RE = re.compile(
    r"^\s*{{\s*([A-Za-z0-9_]+)\s*}}\s*->\s*{{\s*([A-Za-z0-9_]+)\s*}}\s*$"
)
CONDITION_LINE_RE = re.compile(
    r"^\s*({%\s*tr\s+if\s+(?:not\s+)?[A-Za-z0-9_]+\s*%})"
    r"\s*->\s*"
    r"({%\s*tr\s+if\s+(?:not\s+)?[A-Za-z0-9_]+\s*%})\s*$"
)
CONDITION_TOKEN_RE = re.compile(r"{%\s*tr\s+(if\s+(?:not\s+)?[A-Za-z0-9_]+)\s*%}")
CONDITION_EXPRESSION_RE = re.compile(r"^(if\s+)?(not\s+)?([A-Za-z0-9_]+)$")


@lru_cache(maxsize=1)
def load_placeholder_aliases():
    if not MAPPING_PATH.exists():
        raise FileNotFoundError(f"Не найдена карта placeholder-ов: {MAPPING_PATH}")

    placeholder_aliases = {}
    condition_aliases = {}

    for line in MAPPING_PATH.read_text(encoding="utf-8").splitlines():
        placeholder_match = PLACEHOLDER_LINE_RE.match(line)
        if placeholder_match:
            source_name, canonical_name = placeholder_match.groups()
            previous = placeholder_aliases.get(source_name)
            if previous is not None and previous != canonical_name:
                raise ValueError(f"Для {source_name} задано несколько canonical names")
            placeholder_aliases[source_name] = canonical_name
            continue

        condition_match = CONDITION_LINE_RE.match(line)
        if condition_match:
            source_tag, canonical_tag = condition_match.groups()
            condition_aliases[" ".join(source_tag.split())] = " ".join(canonical_tag.split())

    return placeholder_aliases, condition_aliases


def add_protocol_placeholder_aliases(context):
    placeholder_aliases, condition_aliases = load_placeholder_aliases()
    missing_keys = set(placeholder_aliases) - set(context)
    if missing_keys:
        raise KeyError(
            "В DOCX-контексте отсутствуют исходные keys: "
            + ", ".join(sorted(missing_keys))
        )

    aliases = {}
    for source_name, canonical_name in placeholder_aliases.items():
        aliases[canonical_name] = context[source_name]

    conclusion_source = "rear_fog_a_8_13_2_conclusion"
    if conclusion_source in context:
        aliases["a_8_13_2_conclusion"] = context[conclusion_source]
    if "applicable_6_4" in context:
        # Пункт не применяется — в заключении прочерк, текст причины остается в статусе.
        status_6_4 = context["applicable_6_4"]
        aliases["a_6_4_conclusion"] = (
            "-" if str(status_6_4 or "").startswith("не применяется") else status_6_4
        )

    for source_tag, canonical_tag in condition_aliases.items():
        source_match = CONDITION_TOKEN_RE.fullmatch(source_tag)
        canonical_match = CONDITION_TOKEN_RE.fullmatch(canonical_tag)
        if not source_match or not canonical_match:
            continue

        source_expression = CONDITION_EXPRESSION_RE.match(source_match.group(1))
        canonical_expression = CONDITION_EXPRESSION_RE.match(canonical_match.group(1))
        if not source_expression or not canonical_expression:
            continue

        source_negated, source_name = source_expression.group(2), source_expression.group(3)
        canonical_negated, canonical_name = canonical_expression.group(2), canonical_expression.group(3)
        if source_name not in context:
            raise KeyError(f"В DOCX-контексте отсутствует условие {source_name}")

        condition_value = context_value_to_bool(context[source_name])
        if source_negated:
            condition_value = not condition_value
        aliases[canonical_name] = not condition_value if canonical_negated else condition_value

    context.update(aliases)
    return context
