import re


def highlight_term(text: str, term: str) -> str:
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", text)