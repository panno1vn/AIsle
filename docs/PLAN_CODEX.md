# PLAN_CODEX

Roadmap triển khai simulator. Thứ tự dưới đây là thứ tự phụ thuộc; chỉ đánh dấu hoàn tất khi code, test và tài liệu liên quan cùng đạt.

## Phase 1 — Simulation core

- [x] Task 1.1 — Attenuated Need-Delta
- [x] Task 1.2 — Distance penalty bậc hai
- [x] Task 1.6 — Weighted Random thay Argmax
  - Làm ngay sau 1.1/1.2 vì cùng thay đổi `decide()`.
- [x] Task 1.8 — Test Emotion/Need dynamics
  - Chạy ngay sau 1.1/1.2/1.6 để bắt regression sớm.
- [x] Task 1.5 — Phantom-need event
- [x] Task 1.3 — Poisson spawn
- [x] Task 1.4 — Benchmark và tối ưu nếu cần
- [x] Task 1.9 — Layout Validation
  - Độc lập, có thể xen kẽ trong Phase 1.
- [x] Task 1.10 — GA distribution test
  - Hoàn tất trước UI vì các Task 3.x phụ thuộc GA đúng.
- [ ] Task 1.7 — Intentional Mistake (optional)
  - Không chặn Phase 2; có thể hoãn nếu thiếu thời gian.
  - Trạng thái: chủ động hoãn sau Phase 2; chưa có đặc tả hành vi đủ rõ để bật mặc định.

## Phase 2 — Result, replay và history

- [x] Task 2.0 — Export trajectory đầy đủ
  - Bắt buộc hoàn tất trước 2.1 để history không lưu run thiếu dữ liệu replay.
- [x] Task 2.1 — History storage và API
- [x] Task 2.2 — Chuẩn hóa `SimResult` export

## Phase 3 — UI

- [ ] Task 3.1
- [ ] Task 3.2
- [ ] Task 3.3
- [ ] Task 3.4

Các task UI triển khai tuần tự.

## Phase 4 — Documentation

- [ ] Task 4.1
- [ ] Task 4.2
- [ ] Task 4.3

Documentation có thể cập nhật xen kẽ trong mọi phase.
