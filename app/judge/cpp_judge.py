import os
import time
import subprocess
import tempfile
import re
import shutil
from app.config import CPP_COMPILER

def normalize_output(text: str) -> str:
    """Standard Themis output normalization: strips trailing whitespace and line endings."""
    if not text:
        return ""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)

def run_cpp_online(source_code: str, test_cases: list, problem_code: str = "PROBLEM") -> dict:
    """Online compiler fallback for Vercel/Cloud where local g++ is not installed (via Wandbox GCC)."""
    import urllib.request
    import json

    test_results = []
    passed_count = 0
    total_tests = len(test_cases)

    for idx, tc in enumerate(test_cases, 1):
        inp = tc.get("input_data", "")
        exp_out = tc.get("expected_output", "")
        norm_exp = normalize_output(exp_out)

        payload = {
            "compiler": "gcc-head",
            "code": source_code,
            "stdin": inp,
            "options": "gnu++17"
        }

        try:
            req = urllib.request.Request(
                "https://wandbox.org/api/compile.json",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ThemisEdu/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            exit_code = str(data.get("status", "0"))
            compiler_msg = data.get("compiler_error", "") or data.get("compiler_message", "")
            prog_out = data.get("program_output", "")
            prog_err = data.get("program_error", "")

            # Check if compilation failed
            if exit_code != "0" and compiler_msg and not prog_out:
                return {
                    "status": "CE",
                    "score": 0.0,
                    "max_score": 10.0,
                    "error_message": f"Biên dịch C++ thất bại:\n{compiler_msg}",
                    "test_results": []
                }

            status = "AC" if exit_code == "0" else "RTE"
            user_out = prog_out
            err_msg = prog_err or (compiler_msg if exit_code != "0" else "")
            
            if status == "AC":
                if exp_out:
                    if normalize_output(user_out) == norm_exp:
                        passed_count += 1
                    else:
                        status = "WA"
                else:
                    passed_count += 1

            test_results.append({
                "test_number": idx,
                "folder_name": tc.get("folder_name", f"Test{idx:02d}"),
                "status": status,
                "time_ms": 150,
                "user_output": user_out[:2000],
                "expected_output": exp_out[:2000],
                "error": err_msg
            })

        except Exception as e:
            return {
                "status": "CE",
                "score": 0.0,
                "max_score": 10.0,
                "error_message": f"Máy chủ Cloud không có sẵn g++ và không thể kết nối Cloud Runner ({str(e)}). Vui lòng thử lại hoặc chạy tại Localhost!",
                "test_results": []
            }

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
