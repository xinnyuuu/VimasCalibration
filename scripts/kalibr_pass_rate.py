#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


INPUT_RE = re.compile(r"Number of images:\s*(?P<input>\d+)")
OBSERVATION_RE = re.compile(
    r"Extracted corners for\s+(?P<observations>\d+)\s+images\s+\(of\s+(?P<total>\d+)\s+images\)"
)
PROCESSED_RE = re.compile(r"Processed\s+(?P<total>\d+)\s+images\s+with\s+(?P<used>\d+)\s+images\s+used")


def parse_pass_rates(text: str) -> list[tuple[int, int]]:
    return [(int(m.group("total")), int(m.group("used"))) for m in PROCESSED_RE.finditer(text)]


def parse_observation_rates(text: str) -> list[tuple[int, int]]:
    return [(int(m.group("total")), int(m.group("observations"))) for m in OBSERVATION_RE.finditer(text)]


def parse_input_count(text: str) -> int | None:
    matches = list(INPUT_RE.finditer(text))
    return int(matches[-1].group("input")) if matches else None


def print_rate(label: str, total: int, used: int, name: str) -> None:
    rejected = total - used
    rate = 100.0 * used / total if total else 0.0
    print(label)
    print(f"  total_images: {total}")
    print(f"  {name}: {used}")
    print(f"  rejected:     {rejected}")
    print(f"  pass_rate:    {rate:.2f}%")


def print_log_summary(label: str, text: str) -> bool:
    observation_entries = parse_observation_rates(text)
    if observation_entries:
        total, observations = observation_entries[-1]
        input_count = parse_input_count(text)
        print(label)
        if input_count is not None and input_count != total:
            print(f"  input_images:        {input_count}")
        print(f"  total_images:        {total}")
        print(f"  kalibr_observations: {observations}")
        print(f"  rejected:            {total - observations}")
        print(f"  observation_rate:    {100.0 * observations / total if total else 0.0:.2f}%")
        return True

    processed_entries = parse_pass_rates(text)
    if processed_entries:
        total, used = processed_entries[-1]
        print_rate(label, total, used, "used_images")
        return True

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Kalibr image pass rate from calibration terminal logs.")
    parser.add_argument("logs", nargs="*", help="Kalibr log file(s). If omitted, read stdin.")
    args = parser.parse_args()

    if not args.logs:
        if not print_log_summary("stdin", sys.stdin.read()):
            raise SystemExit("error: no Kalibr observation or pass-rate lines found on stdin")
        return

    had_result = False
    for log in args.logs:
        path = Path(log)
        if print_log_summary(str(path), path.read_text(encoding="utf-8", errors="replace")):
            had_result = True
        else:
            print(f"{path}: no Kalibr observation or pass-rate lines found")
    if not had_result:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
