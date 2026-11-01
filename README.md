# THEMIS EDU - Nền Tảng Học & Thi Tin Học Trực Tuyến

Hệ thống chấm tự động C++ và Python theo định dạng chuẩn bộ test Themis (10 test cases), phân tích chính xác từng dòng lỗi thẻ HTML, kiểm tra cấu trúc DOM, tính thang điểm 10.0 và cập nhật bảng xếp hạng thi đua thời gian thực.

## Tính năng nổi bật
- **Biên dịch & Chạy thử HTML/CSS/JS:** Kiểm tra cú pháp theo từng dòng, báo lỗi thẻ chưa đóng hoặc sai vị trí, khung Live Preview trực tiếp nền trắng chuẩn xác.
- **Môi trường chạy C++ & Python:** Hỗ trợ nhập Custom Input, theo dõi kết quả Output và thời gian thực thi (ms).
- **Chấm thi chuẩn Themis:** Chấm tự động 10 test cases cho C++ và Python, trả về trạng thái `AC`, `WA`, `TLE`.
- **Hệ thống phân loại chuyên đề:** Phân loại theo Lập trình Web, Nhập môn & Cơ bản, Quy hoạch động Ôn thi HSG.
- **Bảng xếp hạng (Leaderboard):** Thống kê điểm số và vinh danh học sinh dẫn đầu.
- **Quản trị giáo viên:** Upload file ZIP đề bài chuẩn Themis (gồm `Test01`, `Test02`...).

## Triển khai nhanh trên Vercel
Dự án đã được cấu hình sẵn file `vercel.json` và `api/index.py` để deploy tức thì lên Vercel Serverless.

```bash
pip install -r requirements.txt
python run.py
```
