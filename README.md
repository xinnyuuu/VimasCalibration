# FourHeadIntrinsics

四目头环独立 USB/UVC 摄像头内参标定工具。当前四路物理顺序：

```text
左侧 -> 左前 -> 右前 -> 右侧
```

对应 camera key：

```text
left_side
left_front
right_front
right_side
```

推荐采集格式：

```text
640x480 YUYV @ 30fps
```

如果相机实际返回 `60 fps`，也可以继续做内参采图；关键是同一次实验内保持同一分辨率、格式和标定板参数。

## 1. 环境

```bash
cd ~/lxy/FourHeadIntrinsics
source .venv/bin/activate
```

首次安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## 2. 确认相机节点

```bash
python scripts/list_cameras.py --max-index 12 --require-frame
```

只使用 `read_ok=True` 的 `source=/dev/videoX`。如果 `/dev/videoX` 重启后会变化，可以改用：

```bash
ls -l /dev/v4l/by-path/
```

并把稳定路径填入 [configs/four_head_rig.yaml](configs/four_head_rig.yaml)。

## 3. 多次实验目录结构

现在支持用 `--experiment` 手动指定第几次实验。目录会自动变成：

```text
data/images/<camera>/<experiment>/
data/results/<camera>/<experiment>/<method>/
```

例如左侧第 1 次实验：

```text
data/images/left_side/exp01/
data/results/left_side/exp01/chessboard/
```

左侧第 2 次实验：

```text
data/images/left_side/exp02/
data/results/left_side/exp02/chessboard/
```

这样每次实验都不会覆盖前一次结果。

## 4. 采集某次实验

左侧第 2 次实验示例：

```bash
python scripts/capture_camera.py \
  --source /dev/video2 \
  --camera left_side \
  --experiment exp02 \
  --width 640 \
  --height 480 \
  --fps 30 \
  --fourcc YUYV \
  --max-images 60 \
  --interval 0
```

窗口按键：

```text
空格 / s / Enter  保存一张
a                  开关自动保存
q / ESC            退出
```

如果要自动每 2 秒保存，并且要求画面稳定：

```bash
python scripts/capture_camera.py \
  --source /dev/video2 \
  --camera left_side \
  --experiment exp02 \
  --width 640 \
  --height 480 \
  --fps 30 \
  --fourcc YUYV \
  --max-images 60 \
  --require-still \
  --interval 2
```

旧用法仍然可用。如果你显式传 `--output`，脚本会使用这个目录，而不是自动生成实验目录。

## 5. 标定某次实验

棋盘格，左侧第 2 次实验：

```bash
python scripts/calibrate_camera.py \
  --method chessboard \
  --camera left_side \
  --experiment exp02 \
  --cols 9 \
  --rows 6 \
  --square-size 25.0 \
  --max-error 1.0 \
  --auto-filter
```

这会自动读取：

```text
data/images/left_side/exp02/
```

并写入：

```text
data/results/left_side/exp02/chessboard/calibration.yaml
data/results/left_side/exp02/chessboard/processed/
data/results/left_side/exp02/chessboard/debug/
```

ChArUco 交叉验证：

```bash
python scripts/calibrate_camera.py \
  --method charuco \
  --camera left_side \
  --experiment exp02 \
  --cols 8 \
  --rows 11 \
  --square-size 25.0 \
  --max-error 1.0 \
  --auto-filter
```

旧用法仍然可用。如果你显式传 `--images`、`--output`、`--processed-dir`、`--debug-dir`，脚本会使用这些路径。

## 6. 质量判断

对 `640x480` 图像，主点参考：

```text
cx ≈ 320
cy ≈ 240
```

经验值：

- `RMS < 0.5 px`：较好
- `0.5 <= RMS <= 1.0 px`：可用，但建议看 rejected 图
- `RMS > 1.0 px`：偏高，建议补拍或筛图
- 单张误差 `> 1.0 px`：优先检查该图片

如果 `--auto-filter --max-error 1.0` 后剩余图片少于 8 张，说明这次实验中高质量图片不足。建议重新拍一组，或先用较宽阈值诊断：

```bash
python scripts/calibrate_camera.py \
  --method chessboard \
  --camera left_side \
  --experiment exp02 \
  --cols 9 \
  --rows 6 \
  --square-size 25.0 \
  --max-error 2.5 \
  --auto-filter
```

## 7. 标定板

棋盘格生成：

```bash
python scripts/generate_chessboard.py \
  --cols 10 \
  --rows 7 \
  --square-px 160 \
  --output data/patterns/chessboard_9x6_inner.png
```

这对应标定参数：

```text
--cols 9
--rows 6
```

打印后必须用尺量真实方格边长，`--square-size` 填真实值，例如 `21.5` 或 `25.0`。

## 8. 对比多次实验

每次实验结果都在独立目录里，例如：

```text
data/results/left_side/exp01/chessboard/calibration.yaml
data/results/left_side/exp02/chessboard/calibration.yaml
```

对比时重点看：

- `rms_reprojection_error_px`
- `per_view_error_summary`
- `valid_image_count`
- `camera_matrix` 里的 `fx/fy/cx/cy`
- `dist_coeffs`

最终优先选 RMS 低、主点接近 `(320, 240)`、有效图数量充足、rejected 图原因可解释的一次实验。
