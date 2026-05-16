"""Facebook post content builder."""


def build_text_post(title: str, url: str = "") -> str:
    return "\n".join(part for part in (title.strip(), url.strip()) if part)
