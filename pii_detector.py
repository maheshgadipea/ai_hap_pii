#!/usr/bin/env python3
"""PII detection and masking CLI using commonregex-improved (crim)."""

import sys
import re
import argparse
import crim

# Map each PII type to its regex pattern string from crim
PII_PATTERNS: dict[str, str] = {
    "dates": crim.re_date,
    "times": crim.re_time,
    "phones": crim.re_phone,
    "phones_with_exts": crim.re_phones_with_exts,
    "links": crim.re_link,
    "emails": crim.re_email,
    "ipv4s": crim.re_ipv4,
    "ipv6s": crim.re_ipv6,
    "ips": crim.re_ip_pattern,
    "not_known_ports": crim.re_not_known_ports,
    "prices": crim.re_price,
    "hex_colors": crim.re_hex_color,
    "credit_cards": crim.re_credit_card,
    "visa_cards": crim.re_visa_card,
    "master_cards": crim.re_master_card,
    "btc_addresses": crim.re_btc_address,
    "street_addresses": crim.re_street_address,
    "zip_codes": crim.re_zip_code,
    "po_boxes": crim.re_po_box,
    "ssn_numbers": crim.re_ssn,
    "md5_hashes": crim.re_md5_hashes,
    "sha1_hashes": crim.re_sha1_hashes,
    "sha256_hashes": crim.re_sha256_hashes,
    "isbn13s": crim.re_isbn13,
    "isbn10s": crim.re_isbn10,
    "mac_addresses": crim.re_mac_address,
    "iban_numbers": crim.re_iban_number,
    "git_repos": crim.re_git_repo,
}

# Compile all patterns once at startup
_COMPILED: dict[str, re.Pattern] = {
    name: re.compile(pattern)
    for name, pattern in PII_PATTERNS.items()
}


def mask_stars(value: str, _type: str) -> str:
    return re.sub(r"\S", "*", value)


def mask_partial(value: str, _type: str) -> str:
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "*" * (len(value) - 2) + value[-1]


def mask_placeholder(value: str, pii_type: str) -> str:
    return f"<{pii_type.upper()}>"


def mask_redacted(value: str, pii_type: str) -> str:
    return f"[REDACTED-{pii_type.upper()}]"


MASK_FUNCTIONS = {
    "stars": mask_stars,
    "partial": mask_partial,
    "placeholder": mask_placeholder,
    "redacted": mask_redacted,
}


def find_spans(text: str) -> list[tuple[int, int, str, str]]:
    """Return all non-empty PII spans as (start, end, pii_type, matched_text)."""
    spans = []
    for pii_type, pattern in _COMPILED.items():
        for m in pattern.finditer(text):
            matched = m.group()
            if matched:  # skip empty matches
                spans.append((m.start(), m.end(), pii_type, matched))
    return spans


def resolve_spans(spans: list[tuple[int, int, str, str]]) -> list[tuple[int, int, str, str]]:
    """
    Greedily select non-overlapping spans, preferring longer matches.
    Returns spans sorted by start position.
    """
    # Sort by length descending so longer matches win over shorter overlapping ones
    sorted_spans = sorted(spans, key=lambda s: s[1] - s[0], reverse=True)
    selected: list[tuple[int, int, str, str]] = []
    covered: list[tuple[int, int]] = []

    for span in sorted_spans:
        start, end = span[0], span[1]
        if any(start < c_end and end > c_start for c_start, c_end in covered):
            continue
        selected.append(span)
        covered.append((start, end))

    return sorted(selected, key=lambda s: s[0])


def detect_and_mask(text: str, mode: str) -> tuple[str, dict[str, list[str]]]:
    masker = MASK_FUNCTIONS[mode]

    all_spans = find_spans(text)
    resolved = resolve_spans(all_spans)

    detected: dict[str, list[str]] = {}
    for _, _, pii_type, matched in resolved:
        detected.setdefault(pii_type, []).append(matched)

    # Build masked text in a single pass using resolved span positions
    parts = []
    cursor = 0
    for start, end, pii_type, matched in resolved:
        parts.append(text[cursor:start])
        parts.append(masker(matched, pii_type))
        cursor = end
    parts.append(text[cursor:])

    return "".join(parts), detected


def main():
    parser = argparse.ArgumentParser(description="Detect and mask PII in text.")
    parser.add_argument(
        "--mask",
        choices=["stars", "partial", "placeholder", "redacted"],
        default="partial",
        help="Masking style (default: partial)",
    )
    parser.add_argument("text", nargs="*", help="Text to process (or pipe via stdin)")
    args = parser.parse_args()

    text = " ".join(args.text) if args.text else sys.stdin.read()
    masked_text, detected = detect_and_mask(text, args.mask)

    print("=== Masked Output ===")
    print(masked_text)

    if detected:
        print("\n=== Detected PII ===")
        for pii_type, matches in detected.items():
            print(f"  {pii_type}: {matches}")
    else:
        print("\n=== No PII detected ===")


if __name__ == "__main__":
    main()
