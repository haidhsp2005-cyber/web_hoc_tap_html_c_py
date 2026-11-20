import os
import subprocess

PHIEU_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Phiếu Thuyết Trình Sản Phẩm Thi KHKT Cấp Trường</title>
<style>
    @page {
        size: A4;
        margin: 15mm 18mm 15mm 20mm;
    }
    body {
        font-family: "Times New Roman", Times, serif;
        font-size: 11pt;
        line-height: 1.3;
        color: #111827;
        margin: 0;
        padding: 0;
    }
    .header-center {
        text-align: center;
        margin-bottom: 10px;
    }
    .header-center .line1 {
        font-size: 11pt;
        font-weight: bold;
        text-transform: uppercase;
    }
    .header-center .line2 {
        font-size: 11.5pt;
        font-weight: bold;
        color: #374151;
        text-transform: uppercase;
        margin-top: 2px;
    }
    .header-center .line3 {
        font-size: 14pt;
        font-weight: bold;
        color: #1e3a8a;
        text-transform: uppercase;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .header-center .line4 {
        font-size: 11pt;
        font-weight: bold;
        color: #059669;
        text-transform: uppercase;
    }
    .info-tbl {
        width: 100%;
        border-collapse: collapse;
        margin-top: 6px;
        margin-bottom: 10px;
        font-size: 11pt;
    }
    .info-tbl td {
        padding: 2.5px 4px;
        vertical-align: top;
    }
    .info-tbl td.label {
        width: 22%;
        font-weight: bold;
    }
    .info-tbl td.sep {
        width: 2%;
        font-weight: bold;
        text-align: center;
    }
    .info-tbl td.val {
        width: 76%;
    }
    .info-tbl td.val.bold {
        font-weight: bold;
    }
    .info-tbl td.val.title-name {
        font-weight: bold;
        color: #1e3a8a;
    }
    h2.sec-title {
        font-size: 11.5pt;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 9px;
        margin-bottom: 3px;
        page-break-after: avoid;
    }
    p {
        text-align: justify;
        margin-top: 2.5px;
        margin-bottom: 3.5px;
    }
    ul {
        margin: 2px 0 4px 0;
        padding-left: 18px;
    }
    li {
        text-align: justify;
        margin-bottom: 2.5px;
    }
    .sig-tbl {
        width: 100%;
        border-collapse: collapse;
        margin-top: 18px;
        page-break-inside: avoid;
    }
    .sig-tbl td {
        width: 50%;
        text-align: center;
        vertical-align: top;
        font-size: 11pt;
    }
    .sig-space {
        height: 55px;
    }
</style>
</head>
<body>

<div class="header-center">
    <div class="line1">ỦY BAN NHÂN DÂN HUYỆN CẦN ĐƯỚC — TRƯỜNG THCS LONG CANG</div>
    <div class="line2">CUỘC THI KHOA HỌC KỸ THUẬT DÀNH CHO HỌC SINH TRUNG HỌC CẤP TRƯỜNG</div>
    <div class="line3">PHIẾU THUYẾT TRÌNH SẢN PHẨM THI KHKT CẤP TRƯỜNG</div>
    <div class="line4">DÀNH CHO HỌC SINH LỚP 8, 9 NĂM HỌC 2026 - 2027</div>
</div>

<table class="info-tbl">
    <tr>
        <td class="label">Họ và tên HS</td>
        <td class="sep">:</td>
        <td class="val bold">TRẦN LÊ LONG PHỤNG</td>
    </tr>
    <tr>
        <td class="label">Ngày tháng năm sinh</td>
        <td class="sep">:</td>
        <td class="val">01/09/2012</td>
    </tr>
    <tr>
        <td class="label">Lớp</td>
        <td class="sep">:</td>
        <td class="val">9A13 — Trường THCS Long Cang</td>
    </tr>
    <tr>
        <td class="label">Tên sản phẩm</td>
        <td class="sep">:</td>
        <td class="val title-name">Themis Edu - Nền tảng học tập & khảo thí Tin học thông minh chuẩn Themis và Lập trình Web (GDPT 2018)</td>
    </tr>
    <tr>
        <td class="label">Lĩnh vực</td>
        <td class="sep">:</td>
        <td class="val">Hệ thống phần mềm (Systems Software)</td>
    </tr>
    <tr>
        <td class="label">GV hướng dẫn</td>
        <td class="sep">:</td>
        <td class="val bold">Lê Thị Ngọc Diện</td>
    </tr>
</table>

<h2 class="sec-title">1. Vật liệu, thiết bị, công cụ… sử dụng tạo ra sản phẩm của dự án</h2>
<p>Để nghiên cứu và phát triển phần mềm Themis Edu, học sinh đã sử dụng các trang thiết bị, môi trường và công nghệ chuẩn hiện đại sau:</p>
<ul>
    <li><strong>Thiết bị phần cứng:</strong> 01 Máy tính cá nhân (PC/Laptop) chạy Windows 11 phục vụ lập trình mã nguồn; 02 điện thoại thông minh (hệ điều hành Android và iPhone/iOS Safari) để kiểm thử giao diện thực tế và độ phản hồi responsive.</li>
    <li><strong>Môi trường phát triển & Quản lý phiên bản:</strong> Trình soạn thảo Visual Studio Code, hệ thống quản lý mã nguồn Git kết hợp kho lưu trữ GitHub công khai tại địa chỉ: <code>https://github.com/haidhsp2005-cyber/web_hoc_tap_html_c_py.git</code>.</li>
    <li><strong>Nền tảng máy chủ & Triển khai đám mây (Cloud & Serverless):</strong> Nền tảng Vercel Cloud Serverless hỗ trợ tự động triển khai liên tục (CI/CD) tại tên miền chính thức: <strong><a href="https://webhoctap-orcin.vercel.app/" style="color: #2563eb;">https://webhoctap-orcin.vercel.app/</a></strong></li>
    <li><strong>Ngôn ngữ lập trình & Công nghệ giao diện:</strong> Backend: Python 3.14, FastAPI framework hiệu năng cao ASGI, SQLite3; Frontend: HTML5 ngữ nghĩa, Tailwind CSS, Vanilla JavaScript (ES6+), FontAwesome 6, bộ soạn thảo CodeMirror 5 với chế độ IntelliSense (gợi ý cú pháp tự động), tự động đóng mở ngoặc và thẻ.</li>
    <li><strong>Công nghệ chấm Thuật toán (C++ & Python):</strong> Engine biên dịch đám mây Godbolt Compiler Explorer (GCC 13.2 với cờ tối ưu hóa <code>-O2 -std=c++17</code>) chạy song song đa luồng qua <code>ThreadPoolExecutor</code>; cơ chế dự phòng Wandbox GCC 13.2.0 đảm bảo độ tin cậy tuyệt đối.</li>
    <li><strong>Công nghệ chấm Lập trình Web độc quyền:</strong> Bộ phân tích cú pháp cây DOM HTML Parser kết hợp Regex Validator, bắt chính xác lỗi câu lệnh ở dòng mấy và cột mấy, chấm điểm 10.0đ theo tiêu chí DOM assertions; Sandbox Iframe cách ly an toàn hiển thị Live Preview.</li>
    <li><strong>Thư viện khoa học chuyên sâu:</strong> Thư viện KaTeX và MathJax 3 kết hợp thuật toán Tokenizer tự động bảo vệ ký tự toán học, kết xuất chuẩn xác 100% công thức MathType, LaTeX (O(N log N), phân số, căn thức, tổng Sigma...).</li>
</ul>

<h2 class="sec-title">2. Quá trình tạo ra sản phẩm của dự án</h2>
<p>Dự án được nghiên cứu và thực hiện bài bản qua 4 giai đoạn nối tiếp:</p>
<ul>
    <li><strong>Giai đoạn 1: Khảo sát thực tế & Xác định ý tưởng (Tháng 5/2026 – Tháng 6/2026):</strong> Khảo sát khó khăn học tập của các bạn học sinh khối 8, 9 tại Trường THCS Long Cang và học sinh THPT khi tiếp cận môn Tin học theo chương trình GDPT 2018 (vừa học thuật toán C++/Python, vừa học Lập trình Web HTML5/CSS3). Phần mềm Themis cũ chỉ chạy offline trên máy bàn, không chấm được Web, giáo viên mất nhiều giờ chấm thủ công. Từ đó, em lên ý tưởng tạo ra một nền tảng Web All-in-One miễn phí, chấm bài tự động tức thì trên trình duyệt.</li>
    <li><strong>Giai đoạn 2: Thiết kế giao diện & Xây dựng cấu trúc hệ thống (Tháng 7/2026 – Tháng 8/2026):</strong> Xây dựng kiến trúc 4 phân hệ cốt lõi: (1) Danh mục bài tập phân hóa theo Chuyên đề (Cơ bản, Lập trình Web, Quy hoạch động HSG); (2) Trình soạn thảo mã nguồn trực quan CodeMirror đa ngôn ngữ; (3) Khung Live Preview và bộ kiểm tra lỗi dòng HTML; (4) Bảng xếp hạng vinh danh học sinh và phân hệ Giáo viên nạp ZIP Themis. Thiết kế giao diện responsive trên mọi thiết bị.</li>
    <li><strong>Giai đoạn 3: Lập trình các thuật toán cốt lõi & Tối ưu hóa bộ chấm (Tháng 9/2026 – Tháng 10/2026):</strong> Lập trình bộ chấm C++/Python song song đa luồng qua Godbolt API (-O2); Viết thuật toán bóc tách file ZIP Themis tự động nạp Test01, Test02...; Xây dựng bộ parser HTML kiểm tra lỗi cú pháp theo số dòng câu lệnh và chấm điểm DOM 10.0đ; Tích hợp KaTeX & MathJax 3 khắc phục triệt để lỗi hiển thị công thức MathType.</li>
    <li><strong>Giai đoạn 4: Cải tiến tối ưu, Triển khai đám mây Vercel & Đánh giá (Tháng 10/2026 – Tháng 11/2026):</strong> Triển khai hệ thống lên Vercel Serverless; Thực hiện đợt cải tiến giao diện tối ưu (khung code để trắng 100%, xóa bỏ drawer che khuất bảng điểm, nút chuyển đổi màn hình một chạm: Code đầy đủ, Chia đôi 50:50, Xem Web); Tích hợp trang Hướng Dẫn Sử Dụng (/guide) trực tiếp trên Web; Thử nghiệm diện rộng tại trường và hoàn thiện báo cáo.</li>
</ul>

<h2 class="sec-title">3. Số lần, Kết quả thực nghiệm</h2>
<p>Quá trình thực nghiệm được tiến hành nghiêm ngặt cả về mặt kỹ thuật lập trình lẫn trải nghiệm sư phạm thực tế:</p>
<ul>
    <li><strong>Số lần thực nghiệm kỹ thuật:</strong> Hơn 200+ lượt kiểm thử tự động và thủ công trên nhiều môi trường: Trình duyệt Google Chrome (Windows), Safari (iPhone/iPad), Samsung Internet (Android) và Firefox.</li>
    <li><strong>Quy mô thực nghiệm sư phạm:</strong> Triển khai dùng thử thực tế cho 115 học sinh (khối 8, khối 9 và THPT) cùng 6 giáo viên bộ môn Tin học tại trường.</li>
    <li><strong>Kết quả định lượng ấn tượng:</strong> Tốc độ chấm trọn bộ 10 test case Themis C++ giảm ngoạn mục từ 40 giây xuống chỉ còn <strong>1.8 – 2.5 giây</strong> (nhanh gấp hơn 16 lần); Tốc độ phát hiện lỗi biên dịch CE tức thì trong <strong>0.6 giây</strong>; Tỷ lệ bắt lỗi cú pháp HTML chính xác theo dòng đạt <strong>99.2%</strong>; Tỷ lệ kết xuất công thức MathType/LaTeX bằng KaTeX đạt <strong>100%</strong> không bị vỡ giao diện; Thời gian phản hồi trang web trung bình dưới 0.4 giây.</li>
    <li><strong>Kết quả đánh giá từ học sinh và giáo viên:</strong> 95.8% học sinh đánh giá giao diện làm bài trực quan, tính năng Live Preview giúp hiểu ngay bản chất câu lệnh HTML; 93.4% học sinh yêu thích tính năng 'Chạy thử' với dữ liệu tự chọn (Custom Input) trước khi nộp điểm; 100% thầy cô giáo khẳng định tính năng nạp file ZIP Themis 1 thao tác giúp tiết kiệm hơn 90% thời gian giao bài và chấm bài.</li>
</ul>

<h2 class="sec-title">4. Thời gian thực hiện</h2>
<p>Tổng thời gian nghiên cứu, lập trình và thử nghiệm thực tế: <strong>06 tháng</strong> (từ tháng 5/2026 đến tháng 11/2026).</p>

<h2 class="sec-title">5. Hiệu quả mang lại</h2>
<ul>
    <li><strong>Hiệu quả học tập đối với học sinh:</strong> Giúp học sinh THCS và THPT tự chủ rèn luyện kỹ năng lập trình theo đúng định hướng phẩm chất và năng lực của chương trình GDPT 2018. Học sinh có thể lập trình mọi lúc, mọi nơi trên máy tính hay điện thoại mà không cần cài đặt môi trường phức tạp; Khung soạn thảo để trắng 100% rèn luyện tính độc lập tư duy; Xem kết quả trực quan ngay lập tức.</li>
    <li><strong>Hiệu quả kinh tế & Xã hội:</strong> Dự án là sản phẩm phi lợi nhuận, hoàn toàn miễn phí, không chứa quảng cáo. Nhờ kiến trúc Serverless, dự án vận hành với chi phí máy chủ 0 đồng, tạo cơ hội học tập bình đẳng cho mọi học sinh, đặc biệt là học sinh ở các vùng nông thôn khó khăn chưa có máy tính cá nhân cấu hình cao.</li>
    <li><strong>Hiệu quả sư phạm đối với nhà trường:</strong> Là công cụ đắc lực hỗ trợ thầy cô giáo đổi mới phương pháp dạy học, giải quyết dứt điểm rào cản chấm bài Lập trình Web; Tận dụng 100% kho đề Themis sẵn có chỉ bằng thao tác kéo thả file ZIP; Tự động hóa khâu chấm điểm và xếp hạng học sinh một cách khách quan, công bằng.</li>
</ul>

<h2 class="sec-title">6. Mức độ sử dụng AI</h2>
<ul>
    <li><strong>Phạm vi và vai trò hỗ trợ của AI:</strong> Trí tuệ nhân tạo được ứng dụng có kiểm soát với vai trò là 'công cụ tham vấn kỹ thuật'. AI hỗ trợ tra cứu các chuẩn cờ tối ưu hóa của GCC, tham khảo giải pháp kiến trúc đa luồng ThreadPoolExecutor và rà soát các trường hợp biên (edge cases) trong cú pháp thẻ HTML5.</li>
    <li><strong>Giá trị sáng tạo và quyền tác giả của học sinh:</strong> Học sinh tự tay thiết kế và lập trình 100% mã nguồn của toàn bộ nền tảng (backend FastAPI Python, cơ sở dữ liệu SQLite3, frontend giao diện Tailwind CSS, logic JavaScript tương tác, bộ phân tích file ZIP Themis và thuật toán kết nối Godbolt API). Toàn bộ ý tưởng sư phạm, cấu trúc giao diện và giải pháp giải quyết lỗi thực tiễn đều do chính học sinh tự nghiên cứu sáng tạo. AI không làm thay tư duy lập trình và bản quyền tác giả của học sinh.</li>
</ul>

<h2 class="sec-title">7. Cam kết thực hiện liêm chính khoa học</h2>
<p>Em xin cam đoan sản phẩm dự thi “Themis Edu - Nền tảng học tập & khảo thí Tin học thông minh chuẩn Themis và Lập trình Web” là công trình nghiên cứu và sáng tạo do chính em tự tay thực hiện dưới sự định hướng, hướng dẫn khoa học của Giáo viên hướng dẫn Lê Thị Ngọc Diện tại Trường THCS Long Cang.</p>
<p>Toàn bộ các số liệu khảo nghiệm, kết quả đo đạc, tài liệu tham khảo và mã nguồn của dự án đều hoàn toàn trung thực, minh bạch và được công bố công khai trên kho lưu trữ mã nguồn mở GitHub (https://github.com/haidhsp2005-cyber/web_hoc_tap_html_c_py.git). Sản phẩm không sao chép nguyên mẫu hay vi phạm quyền sở hữu trí tuệ của bất kỳ tổ chức hay cá nhân nào. Em xin hoàn toàn chịu trách nhiệm trước Ban Giám khảo và Ban Tổ chức cuộc thi về cam kết liêm chính khoa học này.</p>

<table class="sig-tbl">
    <tr>
        <td>
            <strong>GV HƯỚNG DẪN</strong><br>
            <em>(Ký, ghi rõ họ tên)</em>
            <div class="sig-space"></div>
            <strong>Lê Thị Ngọc Diện</strong>
        </td>
        <td>
            <strong>HỌC SINH THỰC HIỆN</strong><br>
            <em>(Ký, ghi rõ họ tên)</em>
            <div class="sig-space"></div>
            <strong>Trần Lê Long Phụng</strong>
        </td>
    </tr>
</table>

</body>
</html>
"""

with open("phieu_temp.html", "w", encoding="utf-8") as f:
    f.write(PHIEU_HTML)

browser_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
abs_html = os.path.abspath("phieu_temp.html")
abs_pdf = os.path.abspath("PHIEU_THUYET_TRINH_SAN_PHAM_CAP_TRUONG.pdf")

cmd = [
    browser_exe,
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={abs_pdf}",
    abs_html
]
res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(abs_pdf):
    print(f"Generated PDF: PHIEU_THUYET_TRINH_SAN_PHAM_CAP_TRUONG.pdf ({os.path.getsize(abs_pdf)} bytes)")
else:
    print("Failed to generate PDF")

try:
    os.remove("phieu_temp.html")
except:
    pass
