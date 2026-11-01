import sqlite3
import json
import os
from app.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Topics / Chuyên đề
    cur.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL, -- 'web_dev', 'basic', 'hsg_dp', 'hsg_graph'
        description TEXT,
        icon TEXT DEFAULT 'code'
    )
    """)

    # 2. Problems / Đề bài
    cur.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        statement TEXT NOT NULL,
        input_format TEXT,
        output_format TEXT,
        sample_input TEXT,
        sample_output TEXT,
        allowed_languages TEXT DEFAULT '["cpp", "python", "html"]',
        time_limit_ms INTEGER DEFAULT 1000,
        memory_limit_mb INTEGER DEFAULT 256,
        max_score REAL DEFAULT 10.0,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
    """)

    # 3. Test Cases (Format Themis)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        test_number INTEGER NOT NULL,
        folder_name TEXT,
        input_data TEXT NOT NULL,
        expected_output TEXT NOT NULL,
        is_sample INTEGER DEFAULT 0,
        FOREIGN KEY (problem_id) REFERENCES problems (id)
    )
    """)

    # 4. HTML Criteria (Tiêu chí chấm riêng cho HTML)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS html_criteria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        points REAL DEFAULT 2.0,
        type TEXT DEFAULT 'contains_tag',
        tag TEXT,
        text TEXT,
        keyword TEXT,
        FOREIGN KEY (problem_id) REFERENCES problems (id)
    )
    """)

    # 5. Submissions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        student_name TEXT NOT NULL,
        language TEXT NOT NULL,
        source_code TEXT NOT NULL,
        status TEXT NOT NULL, -- 'AC', 'WA', 'TLE', 'CE', 'RTE', 'PARTIAL'
        score REAL DEFAULT 0.0,
        max_score REAL DEFAULT 10.0,
        details_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id)
    )
    """)

    # 6. Users / Students
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        class_name TEXT DEFAULT '11 Tin'
    )
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()


def seed_initial_data(conn):
    cur = conn.cursor()
    # Check if topics already exist
    cur.execute("SELECT COUNT(*) FROM topics")
    if cur.fetchone()[0] > 0:
        return

    # Seed Topics
    topics_data = [
        ("Lập trình Web - HTML & CSS Cơ bản", "chuyen-de-html", "web_dev", "Làm quen với cấu trúc văn bản, thẻ tiêu đề, bảng biểu, danh sách và form trên trang web.", "globe"),
        ("Nhập môn & Cơ bản", "nhap-mon-co-ban", "basic", "Các bài toán làm quen với cấu trúc rẽ nhánh, vòng lặp và xử lý số học cơ bản.", "terminal"),
        ("Quy hoạch động - Ôn thi HSG", "quy-hoach-dong-hsg", "hsg_dp", "Chuyên đề nâng cao ôn thi Học sinh giỏi các cấp: LIS, Cái túi, Xếp lịch...", "award"),
    ]

    for name, slug, cat, desc, icon in topics_data:
        cur.execute("INSERT INTO topics (name, slug, category, description, icon) VALUES (?, ?, ?, ?, ?)",
                    (name, slug, cat, desc, icon))

    # Seed Problems
    cur.execute("SELECT id, slug FROM topics")
    topic_map = {row["slug"]: row["id"] for row in cur.fetchall()}

    # 1. Problem HTML_01
    html_topic_id = topic_map["chuyen-de-html"]
    cur.execute("""
    INSERT INTO problems (topic_id, code, title, statement, input_format, output_format, sample_input, sample_output, allowed_languages, time_limit_ms, max_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        html_topic_id,
        "HTML_01",
        "Tạo trang Giới thiệu Bản thân và Sở thích",
        """Viết mã nguồn **HTML5** hoàn chỉnh để tạo trang web cá nhân giới thiệu về bản thân.
Trang web phải đảm bảo đúng chuẩn cấu trúc HTML, không có lỗi cú pháp hoặc quên đóng thẻ.

### Yêu cầu chi tiết:
1. Có cấu trúc trang chuẩn: thẻ `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`.
2. Có thẻ `<h1>` chứa tiêu đề giới thiệu (ví dụ: "Giới thiệu bản thân").
3. Có ít nhất một đoạn văn `<p>` giới thiệu tên, trường lớp hoặc quê quán.
4. Có một danh sách không thứ tự `<ul>` liệt kê ít nhất 3 sở thích bằng các thẻ `<li>`.
5. Có một thẻ liên kết `<a>` chứa thuộc tính `href` trỏ đến trang mạng xã hội hoặc website yêu thích.""",
        "Không có input (Mã nguồn HTML hoàn chỉnh)",
        "Giao diện hiển thị trực quan và cấu trúc thẻ đúng tiêu chí",
        "",
        """<!DOCTYPE html>
<html>
<head>
    <title>Gioi thieu ban than</title>
</head>
<body>
    <h1>Gioi thieu ban than</h1>
    <p>Toi la Nguyen Van A, hoc sinh lop 11 Chuyen Tin.</p>
    <ul>
        <li>Lap trinh C++ va Python</li>
        <li>Choi bong da</li>
        <li>Nghe nhac</li>
    </ul>
    <a href="https://google.com">Trang web yeu thich</a>
</body>
</html>""",
        json.dumps(["html"]),
        1000,
        10.0
    ))
    html_p1_id = cur.lastrowid

    # Add HTML Criteria for HTML_01
    criteria_p1 = [
        ("Cấu trúc HTML hợp lệ", "Có đầy đủ thẻ <html> và <body>, không lỗi cú pháp", 2.0, "basic_structure", None, None, None),
        ("Thẻ tiêu đề <h1>", "Có thẻ <h1> chứa tiêu đề", 2.0, "contains_tag", "h1", None, None),
        ("Đoạn văn giới thiệu <p>", "Có thẻ <p> trình bày nội dung", 2.0, "contains_tag", "p", None, None),
        ("Danh sách sở thích <ul> + <li>", "Có danh sách <ul> và các mục <li>", 2.0, "contains_tag", "ul", None, None),
        ("Liên kết <a> với href", "Có thẻ <a> kèm thuộc tính href", 2.0, "contains_tag", "a", None, None),
    ]
    for name, desc, pts, c_type, tag, text, kw in criteria_p1:
        cur.execute("INSERT INTO html_criteria (problem_id, name, description, points, type, tag, text, keyword) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (html_p1_id, name, desc, pts, c_type, tag, text, kw))

    # 2. Problem HTML_02 (Bảng Thời Khóa Biểu)
    cur.execute("""
    INSERT INTO problems (topic_id, code, title, statement, input_format, output_format, sample_input, sample_output, allowed_languages, time_limit_ms, max_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        html_topic_id,
        "HTML_02",
        "Thiết kế Thời khóa biểu học tập bằng Bảng (Table)",
        """Tạo một trang web HTML hiển thị **Thời khóa biểu học tập trong tuần**.
Trang web phải sử dụng đúng thẻ bảng biểu trong HTML và không xảy ra lỗi đóng/mở thẻ lộn xộn.

### Yêu cầu chi tiết:
1. Có thẻ `<h1>` với nội dung "Thời khóa biểu".
2. Sử dụng thẻ `<table>` để tạo bảng dữ liệu.
3. Bảng phải có ít nhất 2 hàng `<tr>` và các ô dữ liệu `<td>` hoặc ô tiêu đề cột `<th>`.
4. Không có lỗi thẻ chưa đóng (đặc biệt các thẻ `<table>`, `<tr>`, `<td>`).""",
        "Không có input (Mã nguồn HTML hoàn chỉnh)",
        "Hiển thị bảng thời khóa biểu",
        "",
        """<!DOCTYPE html>
<html>
<body>
    <h1>Thoi khoa bieu</h1>
    <table border="1">
        <tr>
            <th>Thu</th>
            <th>Mon hoc</th>
        </tr>
        <tr>
            <td>Thu 2</td>
            <td>Tin hoc</td>
        </tr>
    </table>
</body>
</html>""",
        json.dumps(["html"]),
        1000,
        10.0
    ))
    html_p2_id = cur.lastrowid

    cur.execute("INSERT INTO html_criteria (problem_id, name, description, points, type, tag) VALUES (?, ?, ?, ?, ?, ?)",
                (html_p2_id, "Tiêu đề <h1>", "Có thẻ <h1>", 2.0, "contains_tag", "h1"))
    cur.execute("INSERT INTO html_criteria (problem_id, name, description, points, type, tag) VALUES (?, ?, ?, ?, ?, ?)",
                (html_p2_id, "Bảng dữ liệu <table>", "Có thẻ <table> hợp lệ", 4.0, "table", "table"))
    cur.execute("INSERT INTO html_criteria (problem_id, name, description, points, type) VALUES (?, ?, ?, ?, ?)",
                (html_p2_id, "Cú pháp không lỗi", "Các thẻ tr, td, table đóng đúng thứ tự", 4.0, "basic_structure"))

    # 3. Problem TONG2SO (C++ & Python) - Themis Style
    basic_topic_id = topic_map["nhap-mon-co-ban"]
    cur.execute("""
    INSERT INTO problems (topic_id, code, title, statement, input_format, output_format, sample_input, sample_output, allowed_languages, time_limit_ms, max_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        basic_topic_id,
        "TONG2SO",
        "Tính tổng hai số nguyên lớn",
        """Cho hai số nguyên $A$ và $B$. Hãy tính tổng $S = A + B$.

### Dữ liệu vào (Input):
- Một dòng duy nhất chứa hai số nguyên $A, B$ cách nhau bởi dấu cách ($-10^{18} \le A, B \le 10^{18}$).

### Dữ liệu ra (Output):
- Ghi ra một số nguyên duy nhất là tổng $A + B$.""",
        "Dòng duy nhất chứa 2 số nguyên A và B.",
        "Một số nguyên duy nhất là A + B.",
        "15 35",
        "50",
        json.dumps(["cpp", "python"]),
        1000,
        10.0
    ))
    tong_id = cur.lastrowid

    # 10 Themis Test Cases for TONG2SO
    themis_tong_tests = [
        ("1 2", "3"),
        ("10 20", "30"),
        ("100 250", "350"),
        ("-5 15", "10"),
        ("-100 -200", "-300"),
        ("0 0", "0"),
        ("123456789 987654321", "1111111110"),
        ("1000000000 2000000000", "3000000000"),
        ("-999999999999 1000000000000", "1"),
        ("500000000000000000 500000000000000000", "1000000000000000000")
    ]
    for idx, (inp, out) in enumerate(themis_tong_tests, 1):
        cur.execute("INSERT INTO test_cases (problem_id, test_number, folder_name, input_data, expected_output) VALUES (?, ?, ?, ?, ?)",
                    (tong_id, idx, f"Test{idx:02d}", inp, out))

    # 4. Problem DAYCON (LIS - Quy hoạch động HSG)
    dp_topic_id = topic_map["quy-hoach-dong-hsg"]
    cur.execute("""
    INSERT INTO problems (topic_id, code, title, statement, input_format, output_format, sample_input, sample_output, allowed_languages, time_limit_ms, max_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dp_topic_id,
        "DAYCON",
        "Dãy con tăng dài nhất (LIS)",
        """Cho một dãy gồm $N$ số nguyên $A_1, A_2, \dots, A_N$.
Một dãy con của dãy trên được tạo bằng cách xóa bớt một số phần tử (hoặc giữ nguyên) và giữ nguyên thứ tự xuất hiện của các phần tử còn lại.

Hãy tìm độ dài của dãy con tăng nghiêm ngặt dài nhất (mỗi phần tử sau lớn hơn phần tử đứng trước nó).

### Dữ liệu vào (Input):
- Dòng đầu tiên chứa số nguyên dương $N$ ($1 \le N \le 10^5$).
- Dòng thứ hai chứa $N$ số nguyên $A_1, A_2, \dots, A_N$ ($-10^9 \le A_i \le 10^9$).

### Dữ liệu ra (Output):
- Một số nguyên duy nhất là độ dài của dãy con tăng dài nhất.""",
        "Dòng 1: N\nDòng 2: N số nguyên A_1 ... A_N",
        "Độ dài dãy con tăng dài nhất.",
        "6\n1 2 5 3 4 7",
        "4",
        json.dumps(["cpp", "python"]),
        1000,
        10.0
    ))
    daycon_id = cur.lastrowid

    # 10 Themis Test cases for DAYCON
    themis_daycon_tests = [
        ("6\n1 2 5 3 4 7", "4"),
        ("5\n5 4 3 2 1", "1"),
        ("5\n1 2 3 4 5", "5"),
        ("8\n10 9 2 5 3 7 101 18", "4"),
        ("1\n42", "1"),
        ("7\n0 1 0 3 2 3 4", "5"),
        ("4\n7 7 7 7", "1"),
        ("10\n1 3 6 7 9 4 10 5 6 12", "6"),
        ("12\n2 1 5 3 6 4 8 9 7 10 12 11", "7"),
        ("15\n10 22 9 33 21 50 41 60 80 1 2 3 4 5 6", "6")
    ]
    for idx, (inp, out) in enumerate(themis_daycon_tests, 1):
        cur.execute("INSERT INTO test_cases (problem_id, test_number, folder_name, input_data, expected_output) VALUES (?, ?, ?, ?, ?)",
                    (daycon_id, idx, f"Test{idx:02d}", inp, out))

    # Seed Sample Students & Submissions for Leaderboard
    students = [
        ("tranthang", "Trần Thắng", "student", "11 Tin"),
        ("nguyenha", "Nguyễn Thu Hà", "student", "11 Tin"),
        ("leminh", "Lê Quang Minh", "student", "12 Tin"),
        ("hoangnam", "Hoàng Hải Nam", "student", "10 Tin"),
        ("giaovien", "Thầy Nguyễn Văn Toàn (Giáo viên)", "teacher", "Tổ Tin Học")
    ]
    for u, f, r, c in students:
        cur.execute("INSERT OR IGNORE INTO users (username, full_name, role, class_name) VALUES (?, ?, ?, ?)", (u, f, r, c))

    # Seed some sample accepted submissions so Leaderboard looks alive!
    cur.execute("""
    INSERT INTO submissions (problem_id, username, student_name, language, source_code, status, score, max_score, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tong_id, "tranthang", "Trần Thắng", "cpp",
        "#include <iostream>\nusing namespace std;\nint main() { long long a, b; if (cin >> a >> b) cout << a + b; return 0; }",
        "AC", 10.0, 10.0, json.dumps({"passed": 10, "total": 10})
    ))
    cur.execute("""
    INSERT INTO submissions (problem_id, username, student_name, language, source_code, status, score, max_score, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        daycon_id, "tranthang", "Trần Thắng", "cpp",
        "// LIS Solution\n#include <vector>\n//...",
        "AC", 10.0, 10.0, json.dumps({"passed": 10, "total": 10})
    ))
    cur.execute("""
    INSERT INTO submissions (problem_id, username, student_name, language, source_code, status, score, max_score, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        html_p1_id, "nguyenha", "Nguyễn Thu Hà", "html",
        "<!DOCTYPE html><html><body><h1>Gioi thieu</h1><p>...</p><ul><li>A</li></ul><a href='#'>Link</a></body></html>",
        "AC", 10.0, 10.0, json.dumps({"passed": 5, "total": 5})
    ))
    cur.execute("""
    INSERT INTO submissions (problem_id, username, student_name, language, source_code, status, score, max_score, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tong_id, "leminh", "Lê Quang Minh", "python",
        "import sys\na, b = map(int, sys.stdin.read().split())\nprint(a + b)",
        "AC", 10.0, 10.0, json.dumps({"passed": 10, "total": 10})
    ))

    conn.commit()


# Helper query functions
def get_all_topics():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT t.*, COUNT(p.id) as problem_count
    FROM topics t
    LEFT JOIN problems p ON t.id = p.topic_id
    GROUP BY t.id
    ORDER BY t.id
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_problems(topic_slug=None):
    conn = get_connection()
    cur = conn.cursor()
    if topic_slug and topic_slug != "all":
        cur.execute("""
        SELECT p.*, t.name as topic_name, t.slug as topic_slug,
               (SELECT COUNT(*) FROM test_cases tc WHERE tc.problem_id = p.id) as test_count,
               (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id AND s.status = 'AC') as ac_count
        FROM problems p
        JOIN topics t ON p.topic_id = t.id
        WHERE t.slug = ?
        ORDER BY p.id
        """, (topic_slug,))
    else:
        cur.execute("""
        SELECT p.*, t.name as topic_name, t.slug as topic_slug,
               (SELECT COUNT(*) FROM test_cases tc WHERE tc.problem_id = p.id) as test_count,
               (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id AND s.status = 'AC') as ac_count
        FROM problems p
        JOIN topics t ON p.topic_id = t.id
        ORDER BY p.id
        """)
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["allowed_languages"] = json.loads(r["allowed_languages"]) if r["allowed_languages"] else ["cpp", "python"]
    conn.close()
    return rows

def get_problem_detail(code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT p.*, t.name as topic_name, t.slug as topic_slug
    FROM problems p
    JOIN topics t ON p.topic_id = t.id
    WHERE p.code = ?
    """, (code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    problem = dict(row)
    problem["allowed_languages"] = json.loads(problem["allowed_languages"]) if problem["allowed_languages"] else ["cpp", "python"]

    # Fetch test cases (if HTML, fetch criteria)
    cur.execute("SELECT test_number, folder_name, input_data, expected_output FROM test_cases WHERE problem_id = ? ORDER BY test_number", (problem["id"],))
    problem["test_cases"] = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM html_criteria WHERE problem_id = ?", (problem["id"],))
    problem["html_criteria"] = [dict(r) for r in cur.fetchall()]

    conn.close()
    return problem

def save_submission(problem_id: int, username: str, student_name: str, language: str, source_code: str, status: str, score: float, max_score: float, details: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO submissions (problem_id, username, student_name, language, source_code, status, score, max_score, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (problem_id, username, student_name, language, source_code, status, score, max_score, json.dumps(details)))
    sub_id = cur.lastrowid
    conn.commit()
    conn.close()
    return sub_id

def get_leaderboard(topic_slug=None):
    conn = get_connection()
    cur = conn.cursor()
    
    if topic_slug and topic_slug != "all":
        query = """
        SELECT s.username, s.student_name, u.class_name,
               COUNT(DISTINCT CASE WHEN s.status = 'AC' THEN s.problem_id END) as ac_problems,
               ROUND(SUM(best.max_score_per_problem), 1) as total_score
        FROM submissions s
        JOIN users u ON s.username = u.username
        JOIN problems p ON s.problem_id = p.id
        JOIN topics t ON p.topic_id = t.id
        JOIN (
            SELECT username, problem_id, MAX(score) as max_score_per_problem
            FROM submissions
            GROUP BY username, problem_id
        ) best ON s.username = best.username AND s.problem_id = best.problem_id
        WHERE t.slug = ?
        GROUP BY s.username
        ORDER BY total_score DESC, ac_problems DESC
        """
        cur.execute(query, (topic_slug,))
    else:
        query = """
        SELECT s.username, s.student_name, u.class_name,
               COUNT(DISTINCT CASE WHEN s.status = 'AC' THEN s.problem_id END) as ac_problems,
               ROUND(SUM(best.max_score_per_problem), 1) as total_score
        FROM submissions s
        JOIN users u ON s.username = u.username
        JOIN (
            SELECT username, problem_id, MAX(score) as max_score_per_problem
            FROM submissions
            GROUP BY username, problem_id
        ) best ON s.username = best.username AND s.problem_id = best.problem_id
        GROUP BY s.username
        ORDER BY total_score DESC, ac_problems DESC
        """
        cur.execute(query)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
