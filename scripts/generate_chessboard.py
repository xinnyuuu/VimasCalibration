#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a printable chessboard pattern.")
    parser.add_argument("--cols", type=int, default=10, help="Number of black/white squares horizontally.")
    parser.add_argument("--rows", type=int, default=7, help="Number of black/white squares vertically.")
    parser.add_argument("--square-px", type=int, default=160)
    parser.add_argument("--margin-px", type=int, default=160)
    parser.add_argument("--output", default="data/patterns/chessboard_9x6_inner.png")
    args = parser.parse_args()

    board = np.full(
        (args.rows * args.square_px + 2 * args.margin_px, args.cols * args.square_px + 2 * args.margin_px),
        255,
        dtype=np.uint8,
    )
    for row in range(args.rows):
        for col in range(args.cols):
            if (row + col) % 2 == 0:
                y0 = args.margin_px + row * args.square_px
                x0 = args.margin_px + col * args.square_px
                board[y0 : y0 + args.square_px, x0 : x0 + args.square_px] = 0
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), board)
    print(f"wrote {out}; inner corners are {args.cols - 1}x{args.rows - 1}")


if __name__ == "__main__":
    main()
