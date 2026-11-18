# Báo cáo cá nhân — 2A202604122 DoQuangVinh

## 1. Thông tin thành viên

- Họ tên: Đỗ Quang Vinh
- MSSV: 2A202604122
- Email:
- GitHub: quangvinh12a1

## 2. Phần việc phụ trách

Integration, ba shape workflow/single/orchestrator, test, benchmark, crash suite và báo cáo nhóm.

## 3. Đóng góp cụ thể

- Hoàn thiện `workflow.py` với luồng đọc claim/order, tính quote bằng code và gọi host.
- Hoàn thiện `single.py` bằng ReAct tối đa 8 bước, chỉ cho phép tool đọc.
- Hoàn thiện `orchestrator.py` bằng handoff sanitize và investigator read-only.
- Thêm test trace xác nhận không ghi `principal_id` hoặc secret.
- Chạy public matrix, cổng host mặc định, handoff/crash và benchmark.
- Commit kỹ thuật chính: `5b0fbc0`.

## 4. Bằng chứng

- `R-workflow-C-001-s11`
- Public workflow: 62 student tests passed.
- Public single: 62 student tests passed.
- Public orchestrator: 62 student tests passed.
- Cổng host mặc định: 54 passed.
- Crash suite: 20/20.
- Benchmark: `src/reports/benchmark.json`.

## 5. Công cụ AI đã dùng

Dùng Copilot SDK trong VS Code để phân tích code, sửa implementation, tạo test và kiểm tra báo cáo. Mọi thay đổi được kiểm tra bằng pytest và benchmark.

## 6. Tự đánh giá

Đã triển khai ba shape, đảm bảo ranh giới code/model và host-only write, và chọn workflow theo số liệu so cùng corpus/seed.
