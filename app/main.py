import os
import shutil
import tempfile
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

# Mount static files and templates
static_dir = os.path.join(BASE_DIR, "app", "static")
templates_dir = os.path.join(BASE_DIR, "app", "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
def on_startup():
    init_db()

# ==================== PAGE ROUTES ====================

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
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này.")
    return templates.TemplateResponse(request=request, name="solve.html", context={
        "problem": problem
    })

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request, topic: Optional[str] = None):
    topics = get_all_topics()
    ranking = get_leaderboard(topic_slug=topic)
    return templates.TemplateResponse(request=request, name="leaderboard.html", context={
        "topics": topics,
        "ranking": ranking,
        "current_topic": topic or "all"
    })

@app.get("/compile-html", response_class=HTMLResponse)
async def compile_html_page(request: Request):
    """Standalone live HTML/CSS compiler and linter."""
    return templates.TemplateResponse(request=request, name="compiler_html.html", context={})

@app.get("/run-cpp", response_class=HTMLResponse)
async def run_cpp_page(request: Request):
    """Standalone C++ compiler and runner."""
    return templates.TemplateResponse(request=request, name="compiler_code.html", context={"lang": "cpp"})

@app.get("/run-python", response_class=HTMLResponse)
async def run_python_page(request: Request):
    """Standalone Python runner."""
    return templates.TemplateResponse(request=request, name="compiler_code.html", context={"lang": "python"})

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
    lang = req.language.lower()
    source = req.source_code.strip()
    
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
    return {
        "status": first_res.get("status", "DONE"),
        "time_ms": first_res.get("time_ms", 0),
        "output": first_res.get("user_output", ""),
        "error": res.get("error_message") or first_res.get("error", "")
    }


@app.post("/api/teacher/add-problem-themis")
async def api_add_problem_themis(
    code: str = Form(...),
    title: str = Form(...),
    topic_id: int = Form(...),
    statement: str = Form(...),
    time_limit_ms: int = Form(1000),
    allowed_langs: str = Form("cpp,python"),
    themis_zip: Optional[UploadFile] = File(None),
    manual_tests: Optional[str] = Form(None)
):
    """Teacher endpoint to create a problem with Themis ZIP tests."""
    conn = get_connection()
    cur = conn.cursor()

    langs_list = [l.strip() for l in allowed_langs.split(",") if l.strip()]

    try:
        cur.execute("""
        INSERT INTO problems (topic_id, code, title, statement, allowed_languages, time_limit_ms, max_score)
        VALUES (?, ?, ?, ?, ?, ?, 10.0)
        """, (topic_id, code.upper(), title, statement, str(langs_list).replace("'", '"'), time_limit_ms))
        prob_id = cur.lastrowid

        parsed_tests = []
        if themis_zip and themis_zip.filename:
            # Save uploaded zip temporarily
            temp_zip = os.path.join(UPLOAD_DIR, f"{code}_{themis_zip.filename}")
            with open(temp_zip, "wb") as buffer:
                shutil.copyfileobj(themis_zip.file, buffer)
            
            parsed_tests = parse_themis_zip(temp_zip)
            try:
                os.remove(temp_zip)
            except:
                pass

        # If manual tests provided or parsed from zip
        if parsed_tests:
            for tc in parsed_tests:
                cur.execute("""
                INSERT INTO test_cases (problem_id, test_number, folder_name, input_data, expected_output)
                VALUES (?, ?, ?, ?, ?)
                """, (prob_id, tc["test_number"], tc.get("folder_name", f"Test{tc['test_number']:02d}"), tc["input_data"], tc["expected_output"]))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo đề bài: {str(e)}")

    conn.close()
    return {"status": "SUCCESS", "problem_id": prob_id, "test_cases_imported": len(parsed_tests)}
