#!/usr/bin/env python3
"""Unified PII and HAP detection CLI."""

import sys
import argparse
from pii_detector import detect_and_mask
from hap_detector import analyze


def print_pii(text: str, mask_mode: str) -> None:
    masked_text, detected = detect_and_mask(text, mask_mode)
    print("=== PII Masked Output ===")
    print(masked_text)
    if detected:
        print("\n=== Detected PII ===")
        for pii_type, matches in detected.items():
            print(f"  {pii_type}: {matches}")
    else:
        print("\n=== No PII detected ===")


def print_hap(text: str, threshold: float) -> None:
    result = analyze(text, threshold)
    print("=== HAP Analysis ===")
    for label, score in result["scores"].items():
        flag = "  [FLAGGED]" if label in result["flagged"] else ""
        print(f"  {label:<25} {score:.4f}{flag}")
    status = "FLAGGED" if result["is_hap"] else "CLEAN"
    print(f"\nOverall: {status} (threshold: {threshold})")


def get_text(args) -> str:
    return " ".join(args.text) if args.text else sys.stdin.read()


def main():
    parser = argparse.ArgumentParser(description="Detect PII and HAP in text.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # pii subcommand
    pii_p = subparsers.add_parser("pii", help="Detect and mask PII")
    pii_p.add_argument(
        "--mask",
        choices=["stars", "partial", "placeholder", "redacted"],
        default="partial",
        help="Masking style (default: partial)",
    )
    pii_p.add_argument("text", nargs="*", help="Text to process (or pipe via stdin)")

    # hap subcommand
    hap_p = subparsers.add_parser("hap", help="Detect hate, abuse, and profanity")
    hap_p.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Flag score threshold (default: 0.5)",
    )
    hap_p.add_argument("text", nargs="*", help="Text to process (or pipe via stdin)")

    # both subcommand
    both_p = subparsers.add_parser("both", help="Run PII masking and HAP analysis")
    both_p.add_argument(
        "--mask",
        choices=["stars", "partial", "placeholder", "redacted"],
        default="partial",
    )
    both_p.add_argument("--threshold", type=float, default=0.5)
    both_p.add_argument("text", nargs="*", help="Text to process (or pipe via stdin)")

    args = parser.parse_args()
    text = get_text(args)

    if args.mode == "pii":
        print_pii(text, args.mask)
    elif args.mode == "hap":
        print_hap(text, args.threshold)
    elif args.mode == "both":
        print_pii(text, args.mask)
        print()
        print_hap(text, args.threshold)


if __name__ == "__main__":
    main()
