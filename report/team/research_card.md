# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency*, slide 44 và 59 trong tài liệu Lab 8; loại bằng chứng: benchmark guidance. Tài liệu lab có tại [docs/bonus_topics.md](../../docs/bonus_topics.md); URL paper công khai không được repo cung cấp. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Chênh lệch efficiency có thể đến từ cách benchmark được thiết kế; vì vậy kết luận về topology cần giữ cố định runtime, model, tool và baseline rồi chỉ đổi cấu trúc agent. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận nguồn áp dụng cho đánh giá multi-agent; lab không thể khẳng định hiệu năng của model sản xuất. Benchmark này dùng MockLLM, 14 claim public, 5 seed và giá mô phỏng. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi giữ cố định corpus, seed, giá, tool, evaluator và MockLLM, thay đổi topology từ workflow sang single/orchestrator/swarm không làm giảm pass rate; swarm có thể có variance cao hơn và cost/success cao hơn do yếu tố multi-agent. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Ablation topology 4 shape trên cùng ablation: MockLLM; 14 claim `C-001`–`C-014`; seed `11,22,33,44,55`; `as_of=2026-11-15`; bảng giá trong `config/pricing.yaml`; cùng tool, host policy, evaluator và fresh SQLite cho mỗi trial. Biến duy nhất thay đổi là shape: `workflow → single → orchestrator → swarm`. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Dự kiến seed 55 làm swarm tin delay trong ticket thay vì order row và tạo sai một trial. Đo pass rate, pass^5, variance theo seed, cost/success, mean/p95 steps, secret leak và approval bypass. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: 280 trial chạy trên 4 shape × 14 claim × 5 seed; dữ liệu tại [benchmark.json](../../src/reports/benchmark.json). Các run id theo mẫu `R-{shape}-{claim_id}-s{seed}`, ví dụ `R-workflow-C-001-s11`, `R-swarm-C-002-s55`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:

  | Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
  |---|---:|---:|---:|---:|---:|---:|
  | workflow | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 27.8571 | 3.786 / 4 |
  | single | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 47.2143 | 4.571 / 5 |
  | orchestrator | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 55.7143 | 3.786 / 4 |
  | swarm | 0.985714 (69/70) | 0.928571 | 0.928571–1.000 | 0.0008163265 | 49.5669 | 2.800 / 3 |

  Hypothesis **đúng trên bộ public**: ba shape không agent/multi-agent có topology đều đạt pass 100%; swarm có một trial sai ở seed 55 và pass^5 giảm từ 1.000 xuống 0.928571. So với workflow baseline, swarm có cost/success cao hơn 21.7098 VND mô phỏng (49.5669–27.8571) và variance lớn hơn; song mean/p95 steps của swarm thấp hơn (2.800/3 so với 3.786/4). Không thể kết luận thêm multi-agent cải thiện pass hoặc cost từ kết quả này: public suite không tạo miss nào cho workflow/single/orchestrator, còn swarm miss đúng seed cụ thể.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`; corpus public không chứng minh hidden benchmark hoặc hiệu năng thực tế. Cost là chi phí mô phỏng VND, không phải giá API. Không sửa benchmark JSON để đạt kết quả mong muốn.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
