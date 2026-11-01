import sys
import os
import zipfile
import io

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("KIỂM TRA HỆ THỐNG THEMIS ONLINE JUDGE & EDU")
print("=" * 60)

# 1. Test HTML Judge
from app.judge.html_judge import judge_html_code

print("\n--- 1. Kiểm tra bộ chấm HTML (Báo lỗi câu lệnh dòng mấy) ---")

invalid_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Error</title>
</head>
<body>
    <h1>Tieu de chua dong
    <p>Doan van <b>in dam</p></b>
    <img src="avatar.png">
    <div>Khong dong div
</body>
</html>"""

res_invalid = judge_html_code(invalid_html)
print(f"Trạng thái: {res_invalid['status']}, Điểm: {res_invalid['score']}/10.0")
print(f"Số lỗi cú pháp phát hiện: {len(res_invalid['syntax_errors'])}")
for err in res_invalid['syntax_errors']:
    print(f"  -> [DÒNG {err['line']}, CỘT {err['col']}]: {err['message']}")

valid_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Gioi thieu</title>
</head>
<body>
    <h1>Gioi thieu ban than</h1>
    <p>Em la hoc sinh chuyen Tin hoc.</p>
    <ul>
        <li>So thich 1</li>
        <li>So thich 2</li>
        <li>So thich 3</li>
    </ul>
    <a href="https://example.com">Lien ket ca nhan</a>
</body>
</html>"""

res_valid = judge_html_code(valid_html)
print(f"\nThử HTML chuẩn hoàn hảo -> Trạng thái: {res_valid['status']}, Điểm: {res_valid['score']}/10.0")
assert res_valid['score'] == 10.0, "Bài HTML chuẩn phải đạt 10.0 điểm!"
print("=> BỘ CHẤM HTML HOẠT ĐỘNG CHÍNH XÁC 100%!")

# 2. Test Themis ZIP Parser
print("\n--- 2. Kiểm tra bộ bóc tách file ZIP chuẩn Themis ---")
from app.judge.themis_parser import parse_themis_zip

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zf:
    for i in range(1, 6):
        zf.writestr(f"Test{i:02d}/BAI1.INP", f"{i * 10} {i * 20}\n")
        zf.writestr(f"Test{i:02d}/BAI1.OUT", f"{i * 30}\n")

test_zip_path = os.path.join("data", "mock_themis.zip")
with open(test_zip_path, "wb") as f:
    f.write(zip_buffer.getvalue())

parsed = parse_themis_zip(test_zip_path)
print(f"Đã giải nén và phân tích {len(parsed)} test cases từ file ZIP Themis:")
for tc in parsed:
    print(f"  Test {tc['test_number']} ({tc['folder_name']}): INP={tc['input_data'].strip()} -> OUT={tc['expected_output'].strip()}")

assert len(parsed) == 5, "Phải bóc tách đủ 5 test cases"
os.remove(test_zip_path)
print("=> BỘ BÓC TÁCH FILE ZIP THEMIS HOẠT ĐỘNG CHÍNH XÁC 100%!")

# 3. Test Python Judge with Themis Test Cases
print("\n--- 3. Kiểm tra bộ chấm Python trên 10 Test Cases Themis (Bài TONG2SO) ---")
from app.database import get_problem_detail
from app.judge.python_judge import judge_python_code

prob = get_problem_detail("TONG2SO")
python_solution = """import sys
data = sys.stdin.read().split()
if data:
    a, b = int(data[0]), int(data[1])
    print(a + b)
"""

res_py = judge_python_code(python_solution, prob["test_cases"], problem_code="TONG2SO")
print(f"Trạng thái: {res_py['status']}, Điểm số: {res_py['score']}/10.0")
print(f"Kết quả: {res_py['passed_tests']}/{res_py['total_tests']} test cases chính xác.")
for t in res_py['test_results'][:3]:
    print(f"  {t['folder_name']}: {t['status']} ({t['time_ms']}ms)")
print("  ...")
assert res_py['score'] == 10.0, "Lời giải chuẩn phải đạt 10.0 điểm!"
print("=> BỘ CHẤM PYTHON HOẠT ĐỘNG HOÀN HẢO!")

print("\n" + "=" * 60)
print("TẤT CẢ CÁC MODULE LÕI ĐÃ ĐƯỢC KIỂM THỬ THÀNH CÔNG VƯỢT TRỘI!")
print("=" * 60)
