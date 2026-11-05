import os
import sys
import shutil
import tempfile

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List

from app.config import BASE_DIR, UPLOAD_DIR
from app.database import (
    init_db, get_all_topics, get_problems, get_problem_detail,
    save_submission, get_leaderboard, get_connection
)
from app.judge import parse_themis_zip, judge_cpp_code, judge_python_code, judge_html_code

app = FastAPI(title="Themis Online Judge & Edu Platform")

# Templates
templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize DB on load to guarantee availability in Vercel Serverless
try:
    init_db()
except Exception as e:
    print(f"Notice initializing database: {e}")

@app.middleware("http")
async def normalize_path_middleware(request: Request, call_next):
    """Ensure paths like /app/main.py or /api or empty paths route properly on Vercel."""
    path = request.scope.get("path", "")
    for prefix in ("/app/main.py", "/api/index.py", "/api"):
        if path == prefix:
            request.scope["path"] = "/"
            break
        elif path.startswith(prefix + "/"):
            request.scope["path"] = path[len(prefix):]
            break
    response = await call_next(request)
    return response

@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print(f"Startup DB init: {e}")

# ==================== PAGE ROUTES ====================

@app.get("", response_class=HTMLResponse, include_in_schema=False)
@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request, topic: Optional[str] = None):
    topics = get_all_topics()
    problems = get_problems(topic_slug=topic)
    return templates.TemplateResponse(request=request, name="index.html", context={
        "topics": topics,
        "problems": problems,
        "current_topic": topic or "all"
    })

@app.get("/problem/{code}", response_class=HTMLResponse)
async def solve_page(request: Request, code: str):
    problem = get_problem_detail(code)
    if not problem:
        raise HTTPException(status_code=404, detail="Bài tập không tồn tại.")
    return templates.TemplateResponse(request=request, name="solve.html", context={
        "problem": problem
    })

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request, topic: Optional[str] = None):
    topics = get_all_topics()
    leaderboard = get_leaderboard(topic_slug=topic)
    return templates.TemplateResponse(request=request, name="leaderboard.html", context={
        "topics": topics,
        "leaderboard": leaderboard,
        "current_topic": topic or "all"
    })

@app.get("/compile-html", response_class=HTMLResponse)
async def compile_html_page(request: Request):
    return templates.TemplateResponse(request=request, name="compiler_html.html", context={})

@app.get("/run-cpp", response_class=HTMLResponse)
async def run_cpp_page(request: Request):
    return templates.TemplateResponse(request=request, name="compiler_code.html", context={
        "lang": "cpp",
        "lang_mode": "cpp",
        "page_title": "Môi Trường Chạy Thử C++ (GCC 14.2 MinGW)",
        "default_code": """#include <iostream>
using namespace std;

int main() {
    cout << "Xin chào các bạn học sinh!" << endl;
    cout << "Đây là môi trường chạy thử C++." << endl;
    return 0;
}"""
    })

@app.get("/run-python", response_class=HTMLResponse)
async def run_python_page(request: Request):
    return templates.TemplateResponse(request=request, name="compiler_code.html", context={
        "lang": "python",
        "lang_mode": "python",
        "page_title": "Môi Trường Chạy Thử Python 3.14 (UTF-8)",
        "default_code": """# Môi trường chạy thử Python trực tiếp
print("Xin chào các bạn học sinh!")
print("Đây là môi trường chạy thử Python 3.14.")
"""
    })

@app.get("/teacher", response_class=HTMLResponse)
async def teacher_page(request: Request):
    topics = get_all_topics()
    problems = get_problems()
    return templates.TemplateResponse(request=request, name="teacher.html", context={
        "topics": topics,
        "problems": problems
    })

# ==================== API ROUTES ====================

class SubmitRequest(BaseModel):
    problem_code: str
    username: str
    student_name: str
    language: str
    source_code: str

@app.post("/api/submit")
async def api_submit(req: SubmitRequest):
    problem = get_problem_detail(req.problem_code)
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập.")

    lang = req.language.lower()
    source = req.source_code.strip()

    if not source:
        raise HTTPException(status_code=400, detail="Mã nguồn không được để trống.")

    judge_result = {}

    if lang == "html":
        criteria = problem.get("html_criteria", [])
        judge_result = judge_html_code(source, criteria)
    elif lang == "cpp":
        test_cases = problem.get("test_cases", [])
        judge_result = judge_cpp_code(
            source_code=source,
            test_cases=test_cases,
            problem_code=problem["code"],
            time_limit_ms=problem["time_limit_ms"]
        )
    elif lang == "python":
        test_cases = problem.get("test_cases", [])
        judge_result = judge_python_code(
            source_code=source,
            test_cases=test_cases,
            problem_code=problem["code"],
            time_limit_ms=problem["time_limit_ms"]
        )
    else:
        raise HTTPException(status_code=400, detail=f"Ngôn ngữ {lang} không được hỗ trợ.")

    # Save submission
    sub_id = save_submission(
        problem_id=problem["id"],
        username=req.username or "hocsinh",
        student_name=req.student_name or "Học sinh",
        language=lang,
        source_code=source,
        status=judge_result.get("status", "WA"),
        score=judge_result.get("score", 0.0),
        max_score=10.0,
        details=judge_result
    )

    judge_result["submission_id"] = sub_id
    return judge_result


class CustomRunRequest(BaseModel):
    language: str
    source_code: str
    custom_input: str

@app.post("/api/run-test")
async def api_run_test(req: CustomRunRequest):
    """Run code with custom input without scoring."""
    lang = (req.language or "").lower().strip()
    source = req.source_code.strip()

    if not source:
        return {"status": "DONE", "time_ms": 0, "output": "", "error": "Mã nguồn đang để trống"}

    # Auto-detect language if missing or invalid
    if not lang or lang not in ("cpp", "python", "html"):
        if "#include" in source:
            lang = "cpp"
        elif "<html" in source.lower() or "<!doctype" in source.lower():
            lang = "html"
        else:
            lang = "python"
    
    if lang == "html":
        # For HTML, run validator
        res = judge_html_code(source)
        return {
            "status": "SUCCESS",
            "output": "HTML hợp lệ" if not res["syntax_errors"] else "Phát hiện lỗi cú pháp",
            "syntax_errors": res["syntax_errors"],
            "syntax_warnings": res["syntax_warnings"]
        }
    
    test_case = [{"folder_name": "CustomTest", "input_data": req.custom_input, "expected_output": ""}]
    if lang == "cpp":
        res = judge_cpp_code(source, test_case)
    elif lang == "python":
        res = judge_python_code(source, test_case)
    else:
        raise HTTPException(status_code=400, detail="Ngôn ngữ không hợp lệ")

    first_res = res["test_results"][0] if res.get("test_results") else {}
    
    error_msg = (
        first_res.get("error") or 
        first_res.get("error_message") or 
        res.get("error_message") or 
        res.get("compile_error") or 
        ""
    )
    output_text = first_res.get("user_output", "")
    status_code = first_res.get("status") or res.get("status", "DONE")
    exec_time = first_res.get("time_ms", 0)

    return {
        "status": status_code,
        "time_ms": exec_time,
        "output": output_text,
        "error": error_msg
    }


@app.post("/api/teacher/add-problem-themis")
async def api_teacher_add_themis(
    title: str = Form(...),
    code: str = Form(...),
    topic_id: int = Form(...),
    statement: str = Form(...),
    input_format: str = Form(""),
    output_format: str = Form(""),
    sample_input: str = Form(""),
    sample_output: str = Form(""),
    allowed_languages: str = Form('["cpp", "python"]'),
    time_limit_ms: int = Form(1000),
    max_score: float = Form(10.0),
    themis_zip: Optional[UploadFile] = File(None)
):
    code = code.strip().upper()
    if not code or not title:
        raise HTTPException(status_code=400, detail="Mã bài và tiêu đề không được để trống.")

    test_cases = []
    if themis_zip and themis_zip.filename:
        # Save ZIP and parse test cases
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        zip_path = os.path.join(UPLOAD_DIR, f"{code}_{themis_zip.filename}")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(themis_zip.file, f)
        
        test_cases = parse_themis_zip(zip_path, problem_code=code)

    # Insert into database
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO problems (topic_id, code, title, statement, input_format, output_format,
                             sample_input, sample_output, allowed_languages, time_limit_ms, max_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic_id, code, title, statement, input_format, output_format,
              sample_input, sample_output, allowed_languages, time_limit_ms, max_score))
        problem_id = cur.lastrowid

        # Insert test cases
        for tc in test_cases:
            cur.execute("""
            INSERT INTO test_cases (problem_id, folder_name, input_data, expected_output, points)
            VALUES (?, ?, ?, ?, ?)
            """, (problem_id, tc["folder_name"], tc["input_data"], tc["expected_output"], tc.get("points", 1.0)))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi khi lưu bài tập: {str(e)}")
    finally:
        conn.close()

    return {"status": "SUCCESS", "message": f"Đã thêm bài {code} với {len(test_cases)} test cases thành công!", "code": code}
