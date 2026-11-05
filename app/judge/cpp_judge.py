import os
import time
import subprocess
import tempfile
import re
import shutil
import urllib.request
import json
import concurrent.futures
from app.config import CPP_COMPILER

def clean_ansi(text: str) -> str:
    """Strips terminal ANSI color escape codes from compiler and runner output."""
    if not text:
        return ""
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)

def normalize_output(text: str) -> str:
    """Standard Themis output normalization: strips trailing whitespace and line endings."""
    if not text:
        return ""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)

def execute_godbolt_single(source_code: str, stdin: str, timeout: int = 12) -> dict:
    """Runs a single C++ execution against Godbolt Compiler Explorer (GCC 13.2 -O2)."""
    t0 = time.time()
    payload = {
        "source": source_code,
        "options": {
            "userArgs": "-O2 -std=c++17",
            "executeParameters": {"stdin": stdin},
            "filters": {"execute": True}
        }
    }
    req = urllib.request.Request(
        "https://godbolt.org/api/compiler/g132/compile",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ThemisEdu/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    elapsed_ms = int((time.time() - t0) * 1000)

    # 1. Check compile error
    compiler_code = data.get("code", 0)
    if compiler_code != 0:
        raw_errs = data.get("stderr") or []
        err_lines = [clean_ansi(x.get("text", "")) for x in raw_errs]
        return {
            "is_ce": True,
            "error_msg": "\n".join(err_lines).strip() or "Lỗi cú pháp C++ (Compilation Error)",
            "time_ms": elapsed_ms
        }

    # 2. Check runtime execution
    exec_res = data.get("execResult", {})
    exec_code = exec_res.get("code", 0)
    stdout_lines = [x.get("text", "") for x in exec_res.get("stdout", [])]
    stderr_lines = [clean_ansi(x.get("text", "")) for x in exec_res.get("stderr", [])]

    return {
        "is_ce": False,
        "exec_code": exec_code,
        "stdout": "\n".join(stdout_lines),
        "stderr": "\n".join(stderr_lines).strip(),
        "time_ms": elapsed_ms
    }

def execute_wandbox_single(source_code: str, stdin: str, timeout: int = 15) -> dict:
    """Fallback runner via Wandbox GCC 13.2.0."""
    t0 = time.time()
    payload = {
        "compiler": "gcc-13.2.0",
        "code": source_code,
        "stdin": stdin,
        "options": "gnu++17"
    }
    req = urllib.request.Request(
        "https://wandbox.org/api/compile.json",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 ThemisEdu/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    elapsed_ms = int((time.time() - t0) * 1000)
    exit_code = str(data.get("status", "0"))
    compiler_msg = data.get("compiler_error", "") or data.get("compiler_message", "")
    prog_out = data.get("program_output", "")
    prog_err = data.get("program_error", "")

    if exit_code != "0" and compiler_msg and not prog_out:
        return {
            "is_ce": True,
            "error_msg": clean_ansi(compiler_msg).strip(),
            "time_ms": elapsed_ms
        }

    return {
        "is_ce": False,
        "exec_code": int(exit_code) if exit_code.isdigit() else 1,
        "stdout": prog_out,
        "stderr": clean_ansi(prog_err or (compiler_msg if exit_code != "0" else "")).strip(),
        "time_ms": elapsed_ms
    }

def run_cpp_online(source_code: str, test_cases: list, problem_code: str = "PROBLEM") -> dict:
    """
    High-speed parallel online compiler for Vercel & Serverless environments.
    1. Tests test case #1 first to catch Compile Errors (CE) within 1.5s.
    2. Runs all remaining test cases concurrently using ThreadPoolExecutor.
    3. Total turnaround for 10 test cases is boosted from ~40s down to ~1.5 - 2.5s.
    """
    total_tests = len(test_cases)
    if total_tests == 0:
        return {
            "status": "AC",
            "score": 10.0,
            "max_score": 10.0,
            "passed_tests": 0,
            "total_tests": 0,
            "test_results": [],
            "summary": "Không có test case"
        }

    # Step 1: Run Test Case #1 using Godbolt (or Wandbox fallback) to check for CE
    use_godbolt = True
    first_tc = test_cases[0]
    first_inp = first_tc.get("input_data", "")

    try:
        first_run = execute_godbolt_single(source_code, first_inp)
    except Exception as e_godbolt:
        use_godbolt = False
        try:
            first_run = execute_wandbox_single(source_code, first_inp)
        except Exception as e_wand:
            return {
                "status": "CE",
                "score": 0.0,
                "max_score": 10.0,
                "error_message": f"Không thể kết nối dịch vụ biên dịch C++ trực tuyến ({e_godbolt}; {e_wand}). Vui lòng kiểm tra lại kết nối mạng!",
                "test_results": []
            }

    # If test #1 failed to compile, immediately return CE
    if first_run.get("is_ce"):
        return {
            "status": "CE",
            "score": 0.0,
            "max_score": 10.0,
            "error_message": f"Biên dịch C++ thất bại:\n{first_run.get('error_msg')}",
            "test_results": []
        }

    # Step 2: Test #1 compiled successfully!
    runner_func = execute_godbolt_single if use_godbolt else execute_wandbox_single

    # Prepare holder for all results
    all_runs = [None] * total_tests
    all_runs[0] = first_run

    # If there are remaining tests, execute them in parallel
    if total_tests > 1:
        def worker(idx_and_tc):
            idx, tc = idx_and_tc
            inp = tc.get("input_data", "")
            try:
                return idx, runner_func(source_code, inp)
            except Exception as ex:
                return idx, {"is_ce": False, "exec_code": 1, "stdout": "", "stderr": f"Lỗi chạy test: {str(ex)}", "time_ms": 100}

        max_workers = min(total_tests - 1, 10)
        remaining_items = list(enumerate(test_cases[1:], start=1))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, res in executor.map(worker, remaining_items):
                all_runs[idx] = res

    # Step 3: Evaluate test results and compute score
    test_results = []
    passed_count = 0

    for idx, (tc, run_data) in enumerate(zip(test_cases, all_runs), 1):
        exp_out = tc.get("expected_output", "")
        norm_exp = normalize_output(exp_out)
        user_out = run_data.get("stdout", "")
        norm_user = normalize_output(user_out)
        exec_code = run_data.get("exec_code", 0)
        err_msg = run_data.get("stderr", "")

        if exec_code != 0:
            status = "RTE"
        elif exp_out:
            if norm_user == norm_exp:
                status = "AC"
                passed_count += 1
            else:
                status = "WA"
        else:
            status = "AC"
            passed_count += 1

        test_results.append({
            "test_number": idx,
            "folder_name": tc.get("folder_name", f"Test{idx:02d}"),
            "status": status,
            "time_ms": run_data.get("time_ms", 50),
            "user_output": user_out[:2000],
            "expected_output": exp_out[:2000],
            "error": err_msg
        })

    final_score = round((passed_count / total_tests) * 10.0, 1) if total_tests else 0.0
    final_status = "AC" if passed_count == total_tests else ("WA" if passed_count == 0 else "PARTIAL")

    return {
        "status": final_status,
        "score": final_score,
        "max_score": 10.0,
        "passed_tests": passed_count,
        "total_tests": total_tests,
        "test_results": test_results,
        "summary": f"Đạt {final_score}/10.0 điểm"
    }

def judge_cpp_code(source_code: str, test_cases: list, problem_code: str = "PROBLEM", time_limit_ms: int = 1000) -> dict:
    """
    Judges C++ source code against a list of test cases.
    """
    if not test_cases:
        return {
            "status": "ERROR",
            "score": 0.0,
            "max_score": 10.0,
            "error_message": "Không tìm thấy bộ test case nào cho bài tập này.",
            "test_results": []
        }

    # Check if local compiler is available
    is_compiler_available = os.path.exists(CPP_COMPILER) or bool(shutil.which(CPP_COMPILER))
    if not is_compiler_available:
        return run_cpp_online(source_code, test_cases, problem_code)

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "solution.cpp")
        exe_file = os.path.join(tmpdir, "solution.exe")

        with open(src_file, "w", encoding="utf-8") as f:
            f.write(source_code)

        # 1. Compilation
        env = os.environ.copy()
        mingw_bin = os.path.dirname(CPP_COMPILER)
        if mingw_bin and os.path.exists(mingw_bin):
            env["PATH"] = mingw_bin + os.pathsep + env.get("PATH", "")

        try:
            compile_proc = subprocess.run(
                [CPP_COMPILER, "-O2", "-static", "-std=c++17", src_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=15,
                env=env
            )
        except Exception as e:
            return {
                "status": "CE",
                "score": 0.0,
                "max_score": 10.0,
                "error_message": f"Lỗi gọi trình biên dịch C++ ({CPP_COMPILER}): {str(e)}",
                "test_results": []
            }

        if compile_proc.returncode != 0:
            return {
                "status": "CE",
                "score": 0.0,
                "max_score": 10.0,
                "error_message": f"Biên dịch thất bại (Compilation Error):\n{compile_proc.stderr}",
                "test_results": []
            }

        # 2. Execute test cases
        test_results = []
        passed_count = 0
        total_tests = len(test_cases)
        time_limit_sec = time_limit_ms / 1000.0

        for idx, tc in enumerate(test_cases, 1):
            inp = tc.get("input_data", "")
            exp_out = tc.get("expected_output", "")
            norm_exp = normalize_output(exp_out)

            inp_filename = os.path.join(tmpdir, f"{problem_code}.INP")
            out_filename = os.path.join(tmpdir, f"{problem_code}.OUT")
            
            with open(inp_filename, "w", encoding="utf-8") as f_in:
                f_in.write(inp)
            if os.path.exists(out_filename):
                try:
                    os.remove(out_filename)
                except:
                    pass

            start_time = time.perf_counter()
            exec_time_ms = 0
            user_output = ""
            status = "AC"
            err_msg = ""

            try:
                proc = subprocess.run(
                    [exe_file],
                    input=inp,
                    capture_output=True,
                    text=True,
                    timeout=time_limit_sec,
                    cwd=tmpdir,
                    env=env
                )
                exec_time_ms = int((time.perf_counter() - start_time) * 1000)

                if os.path.exists(out_filename) and os.path.getsize(out_filename) > 0:
                    with open(out_filename, "r", encoding="utf-8", errors="ignore") as f_out:
                        user_output = f_out.read()
                else:
                    user_output = proc.stdout

                if proc.returncode != 0:
                    status = "RTE"
                    err_msg = f"Runtime Error (Exit Code {proc.returncode}):\n{proc.stderr}"
                else:
                    norm_user = normalize_output(user_output)
                    if exp_out:
                        if norm_user == norm_exp:
                            status = "AC"
                            passed_count += 1
                        else:
                            status = "WA"
                    else:
                        status = "AC"
                        passed_count += 1

            except subprocess.TimeoutExpired:
                exec_time_ms = time_limit_ms
                status = "TLE"
                err_msg = f"Vượt quá thời gian cho phép ({time_limit_ms}ms)"
            except Exception as e:
                status = "RTE"
                err_msg = str(e)

            test_results.append({
                "test_number": idx,
                "folder_name": tc.get("folder_name", f"Test{idx:02d}"),
                "status": status,
                "time_ms": exec_time_ms,
                "user_output": user_output[:2000],
                "expected_output": exp_out[:2000],
                "error": err_msg
            })

        final_score = round((passed_count / total_tests) * 10.0, 1) if total_tests else 0.0
        final_status = "AC" if passed_count == total_tests else ("WA" if passed_count == 0 else "PARTIAL")

        return {
            "status": final_status,
            "score": final_score,
            "max_score": 10.0,
            "passed_tests": passed_count,
            "total_tests": total_tests,
            "test_results": test_results,
            "summary": f"Đạt {final_score}/10.0 điểm ({passed_count}/{total_tests} test cases chính xác)"
        }
