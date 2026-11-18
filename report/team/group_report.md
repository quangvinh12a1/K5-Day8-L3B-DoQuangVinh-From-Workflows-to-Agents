# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: DoQuangVinh
- Thành viên: Đỗ Quang Vinh — MSSV `2A202604122`
- Commit chốt (trùng `report/team/decision_adr.md`): `631bae6`

## 2. Mục tiêu và cách tiếp cận

Nhóm chỉ gồm một thành viên nên đã tự đảm nhận tích hợp repo, ba shape do học viên triển khai và phần benchmark/báo cáo. Thứ tự thực hiện là: workflow làm baseline xác định, single thêm vòng ReAct chỉ đọc, orchestrator thêm handoff sanitize và investigator read-only, cuối cùng chạy public matrix, crash suite và benchmark so 4 shape.

## 3. Giải pháp

**Workflow:** dùng `get_claim_view` để đọc claim, `lookup_order` để kiểm tra ownership/visibility, rồi `compute_compensation` tính quote từ order row và policy hiện hành. Số tiền dương được truyền nguyên vẹn sang `issue_refund`; model không tham gia quyết định.

**Single:** chạy ReAct tối đa 8 bước với `worker=True`. `decide` chỉ được gọi `get_claim_view`, `lookup_order`, `lookup_policy`, `lookup_refund_history` và `compute_compensation`; `issue_refund` bị runtime chặn. Code kiểm tra kết quả điều tra rồi mới gọi host.

**Orchestrator:** tạo handoff `handoff.v1` bằng `make_handoff`, chỉ cấp tool đọc, và truyền handoff cho `run_readonly_investigators`. Handoff đã sanitize, không chứa secret, header hay principal context. Orchestrator nhận quote và gọi host; host mới thực hiện approval, cap theo order và ghi ledger.

Trace ghi claim id, order id, quyết định, quote đã lọc và kết quả host. Không ghi ticket thô, `principal_id`, secret, header, SĐT, địa chỉ, tên hàng hoặc internal note.

## 4. Kết quả

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
|---|---:|---:|---:|---:|---:|---:|
| workflow | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 27.8571 | 3.786 / 4 |
| single | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 47.2143 | 4.571 / 5 |
| orchestrator | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 55.7143 | 3.786 / 4 |
| swarm | 0.985714 (69/70) | 0.928571 | 0.928571–1.000 | 0.0008163265 | 49.5669 | 2.800 / 3 |

Crash suite: `20/20` pass. Secret leak và approval bypass: không phát hiện trên public benchmark.

Hidden benchmark gồm 40 claim × 5 seed do giảng viên chấm riêng. Nhóm chưa biết pass rate hidden, ngưỡng pass ≥ 0.75, hoặc kết quả 3 must-pass hidden. Không coi số liệu public là bằng chứng cho kết quả hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- Cần phân biệt ticket text với order row để không để model tin số delay sai.
- Cần tránh tự trừ refund đã hoàn trước; đã giữ quote đầy đủ và để host thực hiện cap.
- Cần truyền `crash_at` qua host và không bắt `InjectedCrash`, để crash suite kiểm được đúng crash window.
- Trace dễ lộ PII nếu ghi nguyên claim/order row; đã giới hạn payload tối thiểu và thêm test cho `principal_id`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của thành viên duy nhất nằm trong `TEAM.md` và báo cáo cá nhân `report/team/2A202604122_DoQuangVinh.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất và latency là `unavailable`; kết quả không chứng minh hiệu suất API thực. Corpus public chỉ có 14 claim, chưa chứng minh hidden benchmark. Cost là mô phỏng VND. Hướng cải thiện là bổ sung hidden self-check và kiểm định thống kê trên cùng cặp claim/seed.

## 8. Tài liệu tham khảo

- `docs/metrics.md`
- `docs/contracts.md`
- `docs/business_rules.md`
- `docs/bonus_topics.md`
