# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG THEMIS ONLINE JUDGE & EDU

Hệ thống đã được lập trình hoàn thiện với đầy đủ các tính năng theo đúng yêu cầu của bạn:

---

## 🚀 CÁCH KHỞI ĐỘNG VÀ TRẢI NGHIỆM

1. **Cách 1 (Nhanh nhất):**
   - Click đúp chuột vào file `start_server.bat` trong thư mục dự án.

2. **Cách 2 (Bằng dòng lệnh):**
   - Mở Terminal/PowerShell tại thư mục này và gõ:
     ```bash
     python run.py
     ```

3. **Mở trình duyệt Web:**
   - Truy cập địa chỉ: **`http://127.0.0.1:8000`**

---

## 🌟 CÁC CHỨC NĂNG ĐÃ HOÀN THIỆN

### 1. Phân loại theo Chuyên đề học tập
- **Lập trình Web - HTML & CSS Cơ bản:** Học cú pháp thẻ, bảng biểu, danh sách, bố cục trang web.
- **Nhập môn & Cơ bản (C++, Python):** Luyện cấu trúc rẽ nhánh, vòng lặp, xử lý số lớn.
- **Quy hoạch động - Ôn thi HSG (C++, Python):** Các bài toán kinh điển thi HSG như Dãy con tăng dài nhất (LIS), Bài toán cái túi...

### 2. Trình soạn thảo Code Monaco Editor (Chuẩn VS Code)
- Tích hợp trình soạn code Monaco Editor xịn xò:
  - Tự động highlight cú pháp C++, Python, HTML.
  - Phím tắt VS Code (`Ctrl + /`, `Alt + Shift + F`, gợi ý code).
  - Có khung **Chạy thử (Run Test)** với dữ liệu Custom Input trước khi nộp.

### 3. Cơ chế Chấm HTML đặc thù (Báo sai câu lệnh dòng mấy & Tiêu chí)
- **Báo lỗi cú pháp theo dòng:**
  - Hệ thống tự động phân tích từng dòng mã HTML của học sinh.
  - Báo rõ: *`Dòng 8, Cột 25: Đóng thẻ </p> sai vị trí! Thẻ mở gần nhất là <b> ở dòng 8`* hoặc *`Dòng 6: Thẻ <body> chưa được đóng!`*.
- **Kiểm tra tiêu chí đề bài (DOM Assertions):**
  - Kiểm tra xem học sinh đã có thẻ `<h1>`, bảng `<table>`, danh sách `<ul>`, liên kết `<a>` chưa.
- **Khung xem trước trực tiếp (Live Preview):**
  - Bấm nút **"Live Preview"** để xem giao diện web hiển thị ngay lập tức trong khi đang gõ code!
- **Điểm số:** Quy đổi chuẩn thang điểm **10.0 điểm** (trừ điểm nếu có lỗi cú pháp hoặc thiếu tiêu chí).

### 4. Cơ chế Chấm C++ và Python theo bộ Test Themis
- Hỗ trợ cả 2 dạng đọc/ghi dữ liệu:
  - Chuẩn luồng `cin/cout` (hoặc `sys.stdin/print`).
  - Chuẩn file Themis cổ điển: `freopen("BAI1.INP", "r", stdin)` và `freopen("BAI1.OUT", "w", stdout)`.
- Đo thời gian thực thi chính xác (ms) và giới hạn Time Limit.
- Chấm chi tiết từng Test: Báo trạng thái `Accepted (AC)`, `Wrong Answer (WA)`, `Time Limit (TLE)`, `Runtime Error (RTE)`.
- Tính điểm chuẩn **10.0 điểm** (ví dụ giải đúng 8/10 test $\rightarrow$ đạt **8.0 điểm**).

### 5. Bảng xếp hạng Thi đua (Leaderboard)
- Học sinh làm đúng mỗi bài được tích lũy điểm (tối đa 10đ/bài).
- Vinh danh Huy chương Vàng (Top 1), Bạc (Top 2), Đồng (Top 3).
- **Bộ lọc xếp hạng theo chuyên đề:** Có thể xem bảng xếp hạng riêng cho *Chuyên đề HTML*, hoặc bảng xếp hạng *Quy hoạch động HSG*.

### 6. Trang Quản trị Giáo viên & Upload Test Themis
- Truy cập menu **"Quản Trị / Up Test Themis"** (đường dẫn `/teacher`):
  - Nhập tên bài, mã bài, chuyên đề, ngôn ngữ cho phép.
  - Soạn nội dung đề bài (hỗ trợ Markdown và gõ công thức toán $O(N \log N)$ bằng KaTeX).
  - **Upload file ZIP chuẩn Themis:** Giáo viên chỉ cần nộp 1 file zip chứa các thư mục con `Test01`, `Test02`... kèm file `.INP` và `.OUT`, hệ thống tự động giải nén và nạp toàn bộ test vào đề!

---

## 📁 CẤU TRÚC MÃ NGUỒN DỰ ÁN

```
Web hoc va thi tin hoc/
├── app/
│   ├── config.py              # Cấu hình đường dẫn compiler và database
│   ├── database.py            # Cơ sở dữ liệu SQLite & dữ liệu mẫu
│   ├── main.py                # Máy chủ Web FastAPI & API routes
│   ├── judge/
│   │   ├── themis_parser.py   # Bóc tách file ZIP test chuẩn Themis
│   │   ├── cpp_judge.py       # Bộ chấm C++ (g++ 14.2)
│   │   ├── python_judge.py    # Bộ chấm Python 3.14
│   │   └── html_judge.py      # Bộ chấm HTML báo lỗi theo dòng & tiêu chí DOM
│   └── templates/
│       ├── base.html          # Khung giao diện chính (Tailwind CSS, Icons)
│       ├── index.html         # Trang danh sách bài theo chuyên đề
│       ├── solve.html         # Màn hình làm bài (Monaco Editor, Live Preview)
│       ├── leaderboard.html   # Bảng xếp hạng học sinh
│       └── teacher.html       # Trang giáo viên nhập đề & nạp ZIP Themis
├── data/                      # Lưu trữ cơ sở dữ liệu SQLite & test cases
├── start_server.bat           # File click đúp chạy server ngay lập tức
├── test_system.py             # Script kiểm thử tự động toàn bộ hệ thống
└── run.py                     # Script Python chạy server
```
