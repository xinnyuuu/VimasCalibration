#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a printable ChArUco board.")
    parser.add_argument("--cols", type=int, default=8, help="Chess squares horizontally.")
    parser.add_argument("--rows", type=int, default=11, help="Chess squares vertically.")
    parser.add_argument("--square-px", type=int, default=140)
    parser.add_argument("--marker-ratio", type=float, default=0.72)
    parser.add_argument("--margin-px", type=int, default=160)
    parser.add_argument("--output", default="data/patterns/charuco_8x11.png")
    args = parser.parse_args()

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    board = cv2.aruco.CharucoBoard(
        (args.cols, args.rows),
        float(args.square_px),
        float(args.square_px) * args.marker_ratio,
        dictionary,
    )
    image = board.generateImage(
        (args.cols * args.square_px + 2 * args.margin_px, args.rows * args.square_px + 2 * args.margin_px),
        marginSize=args.margin_px,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), image)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
