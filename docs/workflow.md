# 四目头环内参测定流程

1. 用 `scripts/list_cameras.py` 锁定四路 `/dev/video*`。
2. 按物理顺序更新 `configs/four_head_rig.yaml`。
3. 打印棋盘格或 ChArUco，量真实方格边长。
4. 对每一路独立采图，确保标定板覆盖全画面和四角。
5. 先跑棋盘格标定，再视情况跑 ChArUco 交叉验证。
6. 查看 `processed/rejected` 中被拒图片，必要时删除模糊、反光、误检图片后重跑。
7. 用 `scripts/calibrate_rig.py` 导出 `data/results/four_camera_intrinsics.yaml`。
8. 若 `quality_ledger` 中某路为 `review`，按原因补拍或放宽阈值后重新评估。

这个库只做每个独立相机的内参和畸变，不估计四路外参。外参应在固定头环刚体安装后，用多目共同可见标定板或 AprilTag/Charuco 板另行测定。
