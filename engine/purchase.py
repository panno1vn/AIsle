"""
Công thức xác suất mua hàng — đã sửa theo mục A3 của kế hoạch thực thi.
P = sigmoid(a * need_product + b * valence + c). a/b/c là tham số hiệu chỉnh
do nhóm chọn, đã kiểm tra khớp 2 ca mẫu trong A3.
"""
from __future__ import annotations

import math

A_HE_SO_NHU_CAU = 3.0
B_HE_SO_CAM_XUC = 1.5
C_HANG_SO_NEN = -2.0


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def xac_suat_mua_chinh(
    current_need_product: float,
    current_valence: float,
    a: float = A_HE_SO_NHU_CAU,
    b: float = B_HE_SO_CAM_XUC,
    c: float = C_HANG_SO_NEN,
) -> float:
    return sigmoid(a * current_need_product + b * current_valence + c)


def xac_suat_mua_them(current_valence: float, p_base: float = 0.08) -> float:
    valence_normalized = (current_valence + 1) / 2
    return p_base * valence_normalized


if __name__ == "__main__":
    ca1 = xac_suat_mua_chinh(current_need_product=0.8, current_valence=0.0)
    ca2 = xac_suat_mua_chinh(current_need_product=0.2, current_valence=-0.5)
    print(f"Ca 1 (nhu cầu 0.8, cảm xúc trung tính) -> P = {ca1:.3f}  (kỳ vọng ≈0.6)")
    print(f"Ca 2 (nhu cầu 0.2, cảm xúc âm)          -> P = {ca2:.3f}  (kỳ vọng ≈0.1)")
