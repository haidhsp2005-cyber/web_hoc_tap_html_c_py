# KẾ HOẠCH PHÁT TRIỂN NỀN TẢNG WEB HỌC & THI TIN HỌC (ONLINE JUDGE & LMS)

Tài liệu này vạch ra toàn bộ kiến trúc, giải pháp kỹ thuật và lộ trình triển khai chi tiết cho dự án **Web Học và Thi Tin học** dành cho học sinh, hỗ trợ chấm bài tự động theo chuẩn **Themis** (C++, Python) và chấm cú pháp/DOM chuyên sâu cho **HTML**, phân chuyên đề HSG và bảng xếp hạng.

---

## 1. TỔNG QUAN TÍNH NĂNG HỆ THỐNG

- **Quản lý Đề bài & Test:**
  - Nhập file ZIP chuẩn Themis (`Test01`, `Test02`, file `.INP`/`.OUT`).
  - Đề bài hỗ trợ Markdown và công thức toán KaTeX ($O(N \log N)$).
  - Phân loại theo Chuyên đề (Cơ bản, Đồ thị, Quy hoạch động, HTML/CSS...).
- **Giao diện Học sinh (LMS):**
  - Trình soạn thảo Monaco Editor (trải nghiệm như VS Code).
  - Live Preview trực tiếp đối với bài HTML.
  - Chạy thử Custom Input & nhận kết quả chấm thời gian thực (Realtime).
- **Bộ Chấm Bài (Judge Engine):**
  - C++ / Python: Chạy trong môi trường Sandbox cô lập (Docker/Isolate), chống mã độc.
  - HTML: Linter bắt lỗi cú pháp báo sai câu lệnh ở dòng mấy + kiểm tra tiêu chí DOM.
- **Đánh giá & Xếp hạng:**
  - Quy đổi điểm (10 điểm/bài hoặc theo tỷ lệ test passed).
  - Bảng xếp hạng tổng và bảng xếp hạng theo từng chuyên đề độc lập.

---

## 2. LỘ TRÌNH TRIỂN KHAI (ROADMAP)

- **Giai đoạn 1:** Nền tảng cốt lõi, Quản lý tài khoản, Đề bài & Bộ bóc tách ZIP Themis.
- **Giai đoạn 2:** Trình soạn thảo Monaco, Hàng đợi chấm bài Redis, Sandbox C++/Python & Bộ kiểm tra HTML báo lỗi dòng.
- **Giai đoạn 3:** Hệ thống tính điểm (10đ/bài), Bảng xếp hạng theo chuyên đề & Trang cá nhân học sinh.
- **Giai đoạn 4:** Kiểm thử bảo mật sandbox, tối ưu hiệu năng và đóng gói triển khai Docker.
