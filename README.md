# FourHeadIntrinsics

四目头环独立 USB 摄像头内参标定库。它参考 `InnerParameter` 的 OpenCV 棋盘格 / ChArUco 流程，并针对四目头环补上了：

- 本地 UVC 摄像头枚举、分辨率、FPS、MJPG/YUYV 设置。
- 四个独立相机目录：默认按 `left_side`、`left_front`、`right_front`、`right_side` 存图。
- 单路或四路批量内参标定。
- accepted/rejected 角点调试图、重投影误差筛图和质量指标。
- `four_camera_intrinsics.yaml` 汇总导出，格式可直接供后续多目视觉/SLAM 配置读取。

## 1. 环境

```bash
cd ~/lxy/FourHeadIntrinsics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## 2. 确定四路摄像头

```bash
python scripts/list_cameras.py --max-index 12
```

把结果填到 `configs/four_head_rig.yaml`。当前物理顺序是：

```text
左侧 -> 左前 -> 右前 -> 右侧
```

如果某路摄像头暂时不可识别，先只采可用相机；批量四路标定要求四个目录都有足够图片。

## 3. 生成标定板

棋盘格，默认 10x7 方格，也就是 9x6 内角点：

```bash
python scripts/generate_chessboard.py \
  --cols 10 \
  --rows 7 \
  --square-px 160 \
  --output data/patterns/chessboard_9x6_inner.png
```

ChArUco：

```bash
python scripts/generate_charuco.py \
  --cols 8 \
  --rows 11 \
  --square-px 140 \
  --output data/patterns/charuco_8x11.png
```

打印时选 100% 原始比例，不要适应页面。打印后用尺量真实方格边长，后面的 `--square-size` 填这个实际毫米值，例如 `25.0`。

## 4. 建四路图片目录

```bash
python scripts/make_camera_dirs.py --config configs/four_head_rig.yaml
```

默认会得到：

```text
data/images/left_side/
data/images/left_front/
data/images/right_front/
data/images/right_side/
```

## 5. 采集某一路图片

示例：采左侧到 `data/images/left_side`。

```bash
python scripts/capture_camera.py \
  --source /dev/video2 \
  --width 640 \
  --height 480 \
  --fps 30 \
  --fourcc YUYV \
  --output data/images/left_side \
  --prefix left_side \
  --max-images 60 \
  --require-still \
  --interval 2
```

窗口中按空格、`s` 或回车可手动保存，按 `a` 开关自动保存，按 `q` 退出。每一路建议 30 到 60 张。标定板必须覆盖中心、上下左右边缘和四个角落，不要只在画面中央晃一圈。

当前四目头环推荐使用 `640x480 YUYV @ 30fps`。如果相机实际返回 `60 fps`，也可以继续用于内参采图，关键是所有样本保持同一分辨率和格式。

## 6. 单路标定

棋盘格：

```bash
python scripts/calibrate_camera.py \
  --method chessboard \
  --images data/images/left_side \
  --cols 9 \
  --rows 6 \
  --square-size 25.0 \
  --output data/results/left_side/chessboard/calibration.yaml \
  --processed-dir data/results/left_side/chessboard/processed \
  --debug-dir data/results/left_side/chessboard/debug \
  --max-error 1.0 \
  --auto-filter
```

ChArUco：

```bash
python scripts/calibrate_camera.py \
  --method charuco \
  --images data/images/left_side \
  --cols 8 \
  --rows 11 \
  --square-size 25.0 \
  --output data/results/left_side/charuco/calibration.yaml \
  --processed-dir data/results/left_side/charuco/processed \
  --debug-dir data/results/left_side/charuco/debug \
  --max-error 1.0 \
  --auto-filter
```

## 7. 四路批量标定并导出

四个图片目录都采好后：

```bash
python scripts/calibrate_rig.py \
  --config configs/four_head_rig.yaml \
  --images-root data/images \
  --results-root data/results \
  --method chessboard \
  --cols 9 \
  --rows 6 \
  --square-size 25.0 \
  --output data/results/four_camera_intrinsics.yaml
```

输出 YAML 包含：

- `camera_0_left_side` 到 `camera_3_right_side` 的 `camera_matrix` 和 `dist_coeffs`。
- `quality_ledger` 质检台账。
- RMS、单张最大误差、主点偏移等检查。

质检经验值：

- RMS 重投影误差最好小于 `0.5 px`。
- 单张最大误差超过 `1.0 px` 的图片应检查或剔除。
- `640x480` 下主点建议接近 `(320, 240)`，初期可用 `±10` 到 `±20 px` 排查。
- 同型号四路相机的 `fx/fy` 应接近；某一路明显偏差时优先补拍边缘和角落样本。

## 8. 输出结构

```text
data/results/
  left_side/chessboard/calibration.yaml
  left_side/chessboard/processed/accepted/
  left_side/chessboard/processed/rejected/
  ...
  four_camera_intrinsics.yaml
```
