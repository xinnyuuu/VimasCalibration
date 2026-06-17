#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourhead_intrinsics.calibration import (
    CalibrationOptions,
    QualityFilter,
    calibrate_charuco,
    calibrate_chessboard,
)


def make_options(args: argparse.Namespace) -> CalibrationOptions:
    return CalibrationOptions(
        images=Path(args.images),
        output=Path(args.output),
        processed_dir=Path(args.processed_dir),
        debug_dir=Path(args.debug_dir),
        square_size=args.square_size,
        max_error=args.max_error,
        auto_filter=args.auto_filter,
        quality_filter=QualityFilter(
            min_sharpness=args.min_sharpness,
            min_contrast=args.min_contrast,
            min_coverage=args.min_coverage,
            min_brightness=args.min_brightness,
            max_brightness=args.max_brightness,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate one camera from saved images.")
    parser.add_argument("--method", choices=["chessboard", "charuco"], required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--processed-dir", required=True)
    parser.add_argument("--debug-dir", required=True)
    parser.add_argument("--square-size", type=float, required=True)
    parser.add_argument("--max-error", type=float, default=1.0)
    parser.add_argument("--auto-filter", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-sharpness", type=float, default=20.0)
    parser.add_argument("--min-contrast", type=float, default=15.0)
    parser.add_argument("--min-coverage", type=float, default=0.02)
    parser.add_argument("--min-brightness", type=float, default=10.0)
    parser.add_argument("--max-brightness", type=float, default=245.0)
    parser.add_argument("--cols", type=int, default=9, help="Chessboard inner cols or ChArUco square cols.")
    parser.add_argument("--rows", type=int, default=6, help="Chessboard inner rows or ChArUco square rows.")
    parser.add_argument("--marker-ratio", type=float, default=0.72)
    args = parser.parse_args()

    options = make_options(args)
    if args.method == "chessboard":
        result = calibrate_chessboard(args.cols, args.rows, options)
    else:
        result = calibrate_charuco(args.cols, args.rows, args.marker_ratio, options)

    cm = result["camera_matrix"]
    summary = result["per_view_error_summary"]
    print(f"valid images: {result['valid_image_count']}")
    print(f"RMS reprojection error: {result['rms_reprojection_error_px']:.4f} px")
    print(f"mean/median/max per-view error: {summary['mean_px']:.4f}/{summary['median_px']:.4f}/{summary['max_px']:.4f} px")
    print(f"fx={cm[0][0]:.3f}, fy={cm[1][1]:.3f}, cx={cm[0][2]:.3f}, cy={cm[1][2]:.3f}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
