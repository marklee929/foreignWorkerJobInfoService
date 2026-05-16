from __future__ import annotations

from difflib import SequenceMatcher

from ...models import LifeServiceBusiness


def duplicate_score(left: LifeServiceBusiness, right: LifeServiceBusiness) -> float:
    name_score = SequenceMatcher(None, left.business_name.lower(), right.business_name.lower()).ratio()
    phone_score = 1.0 if left.phone and left.phone == right.phone else 0.0
    address_score = SequenceMatcher(None, left.address.lower(), right.address.lower()).ratio() if left.address and right.address else 0.0
    return round(max(name_score * 0.55 + address_score * 0.30 + phone_score * 0.15, phone_score), 4)
