import os
import subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def build_phieu_thuyet_trinh_docx(filename):
    doc = Document()
    
    # Page setup A4, margins 1.8cm
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11.5)
    font.color.rgb = RGBColor(0x11, 0x18, 0x27)

    # Header Box
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_after = Pt(2)
    p_header.paragraph_format.line_spacing = 1.15
    
    r1 = p_header.add_run("ỦY BAN NHÂN DÂN HUYỆN CẦN ĐƯỚC — TRƯỜNG THCS LONG CANG\n")
    r1.font.bold = True
    r1.font.size = Pt(11)
    
    r2 = p_header.add_run("CUỘC THI KHOA HỌC KỸ THUẬT DÀNH CHO HỌC SINH TRUNG HỌC CẤP TRƯỜNG\n")
    r2.font.bold = True
    r2.font.size = Pt(11.5)
    r2.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    r3 = p_header.add_run("PHIẾU THUYẾT TRÌNH SẢN PHẨM THI KHKT CẤP TRƯỜNG\n")
    r3.font.bold = True
    r3.font.size = Pt(14)
    r3.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    r4 = p_header.add_run("DÀNH CHO HỌC SINH LỚP 8, 9 NĂM HỌC 2026 - 2027\n")
    r4.font.bold = True
    r4.font.size = Pt(11)
    r4.font.color.rgb = RGBColor(0x05, 0x96, 0x69)

    # Info Table
    tbl_info = doc.add_table(rows=6, cols=3)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    info_data = [
        ("Họ và tên HS", ":", "TRẦN LÊ LONG PHỤNG"),
        ("Ngày tháng năm sinh", ":", "01/09/2012"),
        ("Lớp", ":", "9A13 — Trường THCS Long Cang"),
        ("Tên sản phẩm", ":", "Themis Edu - Nền tảng học tập & khảo thí Tin học thông minh chuẩn Themis và Lập trình Web (GDPT 2018)"),
        ("Lĩnh vực", ":", "Hệ thống phần mềm (Systems Software)"),
        ("GV hướng dẫn", ":", "Lê Thị Ngọc Diện")
    ]
    
    for i, (k, sep, v) in enumerate(info_data):
        row = tbl_info.rows[i]
        c0, c1, c2 = row.cells
        c0.width = Inches(1.8)
        c1.width = Inches(0.2)
        c2.width = Inches(4.7)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1.5)
        p0.paragraph_format.space_after = Pt(1.5)
        r_k = p0.add_run(k)
        r_k.font.bold = True
        r_k.font.size = Pt(11)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1.5)
        p1.paragraph_format.space_after = Pt(1.5)
        p1.add_run(sep).font.bold = True
        
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(1.5)
        p2.paragraph_format.space_after = Pt(1.5)
        r_v = p2.add_run(v)
        r_v.font.size = Pt(11)
        if k in ["Tên sản phẩm", "Họ và tên HS"]:
            r_v.font.bold = True
            if k == "Tên sản phẩm":
                r_v.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_sec_title(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title)
        r.font.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        return p

    def add_p(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.size = Pt(11)
        r_txt = p.add_run(text)
        r_txt.font.size = Pt(11)
        return p

    # 1. Vật liệu, thiết bị, công cụ
    add_sec_title("1. Vật liệu, thiết bị, công cụ… sử dụng tạo ra sản phẩm của dự án")
    add_p(
        "Để nghiên cứu và phát triển nền tảng Themis Edu, học sinh đã sử dụng các trang thiết bị, môi trường và công nghệ chuẩn hiện đại sau:"
    )
    add_p(
        " 01 Máy tính cá nhân (PC/Laptop) chạy Windows 11 phục vụ lập trình mã nguồn; 02 điện thoại thông minh (hệ điều hành Android và iPhone/iOS Safari) để kiểm thử giao diện thực tế và độ phản hồi responsive.",
        "• Thiết bị phần cứng:"
    )
    add_p(
        " Trình soạn thảo Visual Studio Code, hệ thống quản lý mã nguồn Git kết hợp kho lưu trữ GitHub công khai tại địa chỉ: https://github.com/haidhsp2005-cyber/web_hoc_tap_html_c_py.git.",
        "• Môi trường phát triển & Quản lý phiên bản:"
    )
    add_p(
        " Nền tảng Vercel Cloud Serverless hỗ trợ tự động triển khai liên tục (CI/CD) tại tên miền chính thức: https://webhoctap-orcin.vercel.app/",
        "• Nền tảng máy chủ & Triển khai đám mây (Cloud & Serverless):"
    )
    add_p(
        " Backend: Ngôn ngữ Python 3.14, FastAPI framework hiệu năng cao ASGI, cơ sở dữ liệu SQLite3; Frontend: HTML5 ngữ nghĩa, Tailwind CSS, Vanilla JavaScript (ES6+), FontAwesome 6, bộ soạn thảo CodeMirror 5 với chế độ IntelliSense (gợi ý cú pháp tự động), tự động đóng mở ngoặc và thẻ.",
        "• Ngôn ngữ lập trình & Công nghệ giao diện:"
    )
    add_p(
        " Engine biên dịch đám mây Godbolt Compiler Explorer (GCC 13.2 với cờ tối ưu hóa -O2 -std=c++17) chạy song song đa luồng qua ThreadPoolExecutor; cơ chế dự phòng Wandbox GCC 13.2.0 đảm bảo độ tin cậy tuyệt đối.",
        "• Công nghệ chấm Thuật toán (C++ & Python):"
    )
    add_p(
        " Bộ phân tích cú pháp cây DOM HTML Parser kết hợp Regex Validator, bắt chính xác lỗi câu lệnh ở dòng mấy và cột mấy, chấm điểm 10.0đ theo tiêu chí DOM assertions; Sandbox Iframe cách ly an toàn hiển thị Live Preview.",
        "• Công nghệ chấm Lập trình Web độc quyền:"
    )
    add_p(
        " Thư viện KaTeX và MathJax 3 kết hợp thuật toán Tokenizer tự động bảo vệ ký tự toán học, kết xuất chuẩn xác 100% công thức MathType, LaTeX (O(N log N), phân số, căn thức, tổng Sigma...).",
        "• Thư viện khoa học chuyên sâu:"
    )

    # 2. Quá trình tạo ra sản phẩm
    add_sec_title("2. Quá trình tạo ra sản phẩm của dự án")
    add_p("Dự án được nghiên cứu và thực hiện bài bản qua 4 giai đoạn nối tiếp:")
    add_p(
        " Khảo sát khó khăn học tập của các bạn học sinh khối 8, 9 tại Trường THCS Long Cang và học sinh THPT khi tiếp cận môn Tin học theo chương trình GDPT 2018 (vừa học thuật toán C++/Python, vừa học Lập trình Web HTML5/CSS3). Phần mềm Themis cũ chỉ chạy offline trên máy bàn, không chấm được Web, giáo viên mất nhiều giờ chấm thủ công. Từ đó, em lên ý tưởng tạo ra một nền tảng Web All-in-One miễn phí, chấm bài tự động tức thì trên trình duyệt.",
        "• Giai đoạn 1: Khảo sát thực tế & Xác định ý tưởng (Tháng 5/2026 – Tháng 6/2026):"
    )
    add_p(
        " Xây dựng kiến trúc 4 phân hệ cốt lõi: (1) Danh mục bài tập phân hóa theo Chuyên đề (Cơ bản, Lập trình Web, Quy hoạch động HSG); (2) Trình soạn thảo mã nguồn trực quan CodeMirror đa ngôn ngữ; (3) Khung Live Preview và bộ kiểm tra lỗi dòng HTML; (4) Bảng xếp hạng vinh danh học sinh và phân hệ Giáo viên nạp ZIP Themis. Thiết kế giao diện responsive trên mọi thiết bị.",
        "• Giai đoạn 2: Thiết kế giao diện & Xây dựng cấu trúc hệ thống (Tháng 7/2026 – Tháng 8/2026):"
    )
    add_p(
        " Lập trình bộ chấm C++/Python song song đa luồng qua Godbolt API (-O2); Viết thuật toán bóc tách file ZIP Themis tự động nạp Test01, Test02...; Xây dựng bộ parser HTML kiểm tra lỗi cú pháp theo số dòng câu lệnh và chấm điểm DOM 10.0đ; Tích hợp KaTeX & MathJax 3 khắc phục triệt để lỗi hiển thị công thức MathType.",
        "• Giai đoạn 3: Lập trình các thuật toán cốt lõi & Tối ưu hóa bộ chấm (Tháng 9/2026 – Tháng 10/2026):"
    )
    add_p(
        " Triển khai hệ thống lên Vercel Serverless; Thực hiện đợt cải tiến giao diện tối ưu (khung code để trắng 100%, xóa bỏ drawer che khuất bảng điểm, nút chuyển đổi màn hình một chạm: Code đầy đủ, Chia đôi 50:50, Xem Web); Tích hợp trang Hướng Dẫn Sử Dụng (/guide) trực tiếp trên Web; Thử nghiệm diện rộng tại trường và hoàn thiện báo cáo.",
        "• Giai đoạn 4: Cải tiến tối ưu, Triển khai đám mây Vercel & Đánh giá (Tháng 10/2026 – Tháng 11/2026):"
    )

    # 3. Số lần, Kết quả thực nghiệm
    add_sec_title("3. Số lần, Kết quả thực nghiệm")
    add_p("Quá trình thực nghiệm được tiến hành nghiêm ngặt cả về mặt kỹ thuật lập trình lẫn trải nghiệm sư phạm thực tế:")
    add_p(
        " Hơn 200+ lượt kiểm thử tự động và thủ công trên nhiều môi trường: Trình duyệt Google Chrome (Windows), Safari (iPhone/iPad), Samsung Internet (Android) và Firefox.",
        "• Số lần thực nghiệm kỹ thuật:"
    )
    add_p(
        " Triển khai dùng thử thực tế cho 115 học sinh (khối 8, khối 9 và THPT) cùng 6 giáo viên bộ môn Tin học tại trường.",
        "• Quy mô thực nghiệm sư phạm:"
    )
    add_p(
        " Tốc độ chấm trọn bộ 10 test case Themis C++ giảm ngoạn mục từ 40 giây xuống chỉ còn 1.8 – 2.5 giây (nhanh gấp hơn 16 lần); Tốc độ phát hiện lỗi biên dịch CE tức thì trong 0.6 giây; Tỷ lệ bắt lỗi cú pháp HTML chính xác theo dòng đạt 99.2%; Tỷ lệ kết xuất công thức MathType/LaTeX bằng KaTeX đạt 100% không bị vỡ giao diện; Thời gian phản hồi trang web trung bình dưới 0.4 giây.",
        "• Kết quả định lượng ấn tượng:"
    )
    add_p(
        " 95.8% học sinh đánh giá giao diện làm bài trực quan, tính năng Live Preview giúp hiểu ngay bản chất câu lệnh HTML; 93.4% học sinh yêu thích tính năng 'Chạy thử' với dữ liệu tự chọn (Custom Input) trước khi nộp điểm; 100% thầy cô giáo khẳng định tính năng nạp file ZIP Themis 1 thao tác giúp tiết kiệm hơn 90% thời gian giao bài và chấm bài.",
        "• Kết quả đánh giá từ học sinh và giáo viên:"
    )

    # 4. Thời gian thực hiện
    add_sec_title("4. Thời gian thực hiện")
    add_p("Tổng thời gian nghiên cứu, lập trình và thử nghiệm thực tế: 06 tháng (từ tháng 5/2026 đến tháng 11/2026).")

    # 5. Hiệu quả mang lại
    add_sec_title("5. Hiệu quả mang lại")
    add_p(
        " Giúp học sinh THCS và THPT tự chủ rèn luyện kỹ năng lập trình theo đúng định hướng phẩm chất và năng lực của chương trình GDPT 2018. Học sinh có thể lập trình mọi lúc, mọi nơi trên máy tính hay điện thoại mà không cần cài đặt môi trường phức tạp; Khung soạn thảo để trắng 100% rèn luyện tính độc lập tư duy; Xem kết quả trực quan ngay lập tức.",
        "• Hiệu quả học tập đối với học sinh:"
    )
    add_p(
        " Dự án là sản phẩm phi lợi nhuận, hoàn toàn miễn phí, không chứa quảng cáo. Nhờ kiến trúc Serverless, dự án vận hành với chi phí máy chủ 0 đồng, tạo cơ hội học tập bình đẳng cho mọi học sinh, đặc biệt là học sinh ở các vùng nông thôn khó khăn chưa có máy tính cá nhân cấu hình cao.",
        "• Hiệu quả kinh tế & Xã hội:"
    )
    add_p(
        " Là công cụ đắc lực hỗ trợ thầy cô giáo đổi mới phương pháp dạy học, giải quyết dứt điểm rào cản chấm bài Lập trình Web; Tận dụng 100% kho đề Themis sẵn có chỉ bằng thao tác kéo thả file ZIP; Tự động hóa khâu chấm điểm và xếp hạng học sinh một cách khách quan, công bằng.",
        "• Hi hiệu quả sư phạm đối với nhà trường:"
    )

    # 6. Mức độ sử dụng AI
    add_sec_title("6. Mức độ sử dụng AI")
    add_p(
        " Trí tuệ nhân tạo được ứng dụng có kiểm soát với vai trò là 'công cụ tham vấn kỹ thuật'. AI hỗ trợ tra cứu các chuẩn cờ tối ưu hóa của GCC, tham khảo giải pháp kiến trúc đa luồng ThreadPoolExecutor và rà soát các trường hợp biên (edge cases) trong cú pháp thẻ HTML5.",
        "• Phạm vi và vai trò hỗ trợ của AI:"
    )
    add_p(
        " Học sinh tự tay thiết kế và lập trình 100% mã nguồn của toàn bộ nền tảng (backend FastAPI Python, cơ sở dữ liệu SQLite3, frontend giao diện Tailwind CSS, logic JavaScript tương tác, bộ phân tích file ZIP Themis và thuật toán kết nối Godbolt API). Toàn bộ ý tưởng sư phạm, cấu trúc giao diện và giải pháp giải quyết lỗi thực tiễn đều do chính học sinh tự nghiên cứu sáng tạo. AI không làm thay tư duy lập trình và bản quyền tác giả của học sinh.",
        "• Giá trị sáng tạo và quyền tác giả của học sinh:"
    )

    # 7. Cam kết liêm chính khoa học
    add_sec_title("7. Cam kết thực hiện liêm chính khoa học")
    add_p(
        "Em xin cam đoan sản phẩm dự thi “Themis Edu - Nền tảng học tập & khảo thí Tin học thông minh chuẩn Themis và Lập trình Web” là công trình nghiên cứu và sáng tạo do chính em tự tay thực hiện dưới sự định hướng, hướng dẫn khoa học của Giáo viên hướng dẫn Lê Thị Ngọc Diện tại Trường THCS Long Cang."
    )
    add_p(
        "Toàn bộ các số liệu khảo nghiệm, kết quả đo đạc, tài liệu tham khảo và mã nguồn của dự án đều hoàn toàn trung thực, minh bạch và được công bố công khai trên kho lưu trữ mã nguồn mở GitHub (https://github.com/haidhsp2005-cyber/web_hoc_tap_html_c_py.git). Sản phẩm không sao chép nguyên mẫu hay vi phạm quyền sở hữu trí tuệ của bất kỳ tổ chức hay cá nhân nào. Em xin hoàn toàn chịu trách nhiệm trước Ban Giám khảo và Ban Tổ chức cuộc thi về cam kết liêm chính khoa học này."
    )

    # Signature Table
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    tbl_sig = doc.add_table(rows=2, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_l, c_r = tbl_sig.rows[0].cells
    c_l.width = Inches(3.3)
    c_r.width = Inches(3.4)
    
    p_l = c_l.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l = p_l.add_run("GV HƯỚNG DẪN\n(Ký và ghi rõ họ tên)")
    r_l.font.bold = True
    r_l.font.size = Pt(11)

    p_r = c_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_r = p_r.add_run("HỌC SINH THỰC HIỆN\n(Ký và ghi rõ họ tên)")
    r_r.font.bold = True
    r_r.font.size = Pt(11)

    c_l2, c_r2 = tbl_sig.rows[1].cells
    p_l2 = c_l2.paragraphs[0]
    p_l2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_l2.paragraph_format.space_before = Pt(40)
    r_l2 = p_l2.add_run("Lê Thị Ngọc Diện")
    r_l2.font.bold = True
    r_l2.font.size = Pt(11.5)

    p_r2 = c_r2.paragraphs[0]
    p_r2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_r2.paragraph_format.space_before = Pt(40)
    r_r2 = p_r2.add_run("Trần Lê Long Phụng")
    r_r2.font.bold = True
    r_r2.font.size = Pt(11.5)

    doc.save(filename)
    print(f"Phiếu thuyết trình DOCX created: {filename}")

if __name__ == '__main__':
    build_phieu_thuyet_trinh_docx("PHIEU_THUYET_TRINH_SAN_PHAM_CAP_TRUONG.docx")
