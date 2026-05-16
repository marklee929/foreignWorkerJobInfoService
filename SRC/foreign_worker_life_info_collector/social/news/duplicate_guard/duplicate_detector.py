"""News duplicate detection placeholder."""


def is_duplicate(item, existing_items) -> bool:
    return any(getattr(item, "url", None) == getattr(existing, "url", None) for existing in existing_items)
