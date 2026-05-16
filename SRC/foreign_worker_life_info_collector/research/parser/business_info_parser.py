from __future__ import annotations

from ...models import LifeServiceBusiness, RawSourceData
from .address_parser import parse_address, split_region
from .contact_parser import parse_phone
from .language_parser import parse_languages


def parse_business_info(raw: RawSourceData) -> LifeServiceBusiness:
    text = " ".join([raw.raw_title, raw.raw_content, raw.raw_phone, raw.raw_address])
    phone = raw.raw_phone or parse_phone(text)
    address = raw.raw_address or parse_address(text)
    sido, sigungu = split_region(address)
    business = LifeServiceBusiness(
        business_name=raw.raw_title.strip() or raw.search_keyword,
        category="unclassified",
        phone=phone,
        address=address,
        sido=sido,
        sigungu=sigungu,
        website_url=raw.source_url if raw.source_url.startswith(("http://", "https://")) else "",
    )
    business.languages = parse_languages(text)
    return business
