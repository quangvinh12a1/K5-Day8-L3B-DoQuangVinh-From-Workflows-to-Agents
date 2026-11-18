# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: `631bae6`
- Run id dẫn chứng: `R-workflow-C-001-s11`
- Pass rate / pass^5 / seed min-max / variance: public benchmark `1.000 / 1.000 / 1.000-1.000 / 0.000000`; hidden chưa biết
- Cost per success (mô phỏng, VND): public benchmark `27.8571`; hidden chưa biết
- Crash safety: `20/20 (src/reports/crash.json)`
- Secret leak / approval bypass: public benchmark `0 / 0`; hidden do giảng viên chấm, chưa có kết quả chính thức
- Hidden 40 claim × 5 seed: chưa biết pass rate và kết quả must-pass; không khẳng định đạt ngưỡng pass ≥ 0.75

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng 14 claim public, 5 seed và evaluator cố định, workflow đạt pass rate 1.000 và pass^5 1.000, với variance 0; single và orchestrator cùng đạt 1.000/1.000 nhưng cost/success lần lượt là 47.2143 và 55.7143 VND mô phỏng, cao hơn workflow 27.8571 VND. Vì vậy workflow đáp ứng tiêu chí chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành công việc. Dẫn chứng độc lập gồm run `R-workflow-C-001-s11` trong benchmark và crash suite 20/20.

## Có đáng đổi lấy multi-agent không

Hiện không đáng đổi sang multi-agent: ba shape đều đạt 1.000/1.000, trong khi swarm giảm còn pass 0.985714/pass^5 0.928571 do miss seed 55 và cost/success 49.5669 VND. Quyết định đổi lại nếu workflow trên hidden corpus giảm dưới 0.75 hoặc phát sinh lỗi cần điều tra đặc thù mà model đọc tool có lợi chứng minh; khi đó cần so lại trên cùng hidden corpus, cùng seed, cùng cost và cùng evaluator.

## Trace và bằng chứng

Trace workflow ghi claim id, order id, kết quả lookup đã lọc, quote không có PII, quyết định và refund outcome. Cố ý không ghi `principal_id`, ticket thô, secret, header, số điện thoại, địa chỉ, tên hàng hoặc internal note. Các log hoặc file phụ nằm cùng thư mục trace với tiền tố `run_id` để scanner quét. Cổng host và test trace/chấm evaluator kiểm tra file mới, secret và ledger.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
Hidden 40 claim × 5 seed do giảng viên chấm riêng. Nhóm chưa biết kết quả pass ≥ 0.75, 3 must-pass (không refund thiếu approval; không lộ CANARY; crash ≤ 1 refund) và không suy diễn chúng từ public benchmark.
