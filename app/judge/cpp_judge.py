import os
import time
import subprocess
import tempfile
import re
from app.config import CPP_COMPILER

def normalize_output(text: str) -> str:
    """Standard Themis output normalization: strips trailing whitespace and line endings."""
    if not text:
        return ""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    # remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)

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

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "solution.cpp")
        exe_file = os.path.join(tmpdir, "solution.exe")

        with open(src_file, "w", encoding="utf-8") as f:
            f.write(source_code)

        # 1. Compilation
        env = os.environ.copy()
        mingw_bin = os.path.dirname(CPP_COMPILER)
        env["PATH"] = mingw_bin + ";" + env.get("PATH", "")

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

            # In case the code uses freopen with problem_code (e.g. BAI1.INP)
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

                # Check if output is in stdout or freopen file
                if os.path.exists(out_filename) and os.path.getsize(out_filename) > 0:
                    with open(out_filename, "r", encoding="utf-8", errors="ignore") as f_out:
                        user_output = f_out.read()
                else:
                    user_output = proc.stdout

                if proc.returncode != 0:
                    status = "RTE"
                    err_msg = f"Runtime Error (Mã thoát: {proc.returncode})\n{proc.stderr}"
                else:
                    norm_user = normalize_output(user_output)
                    if norm_user == norm_exp:
                        status = "AC"
                        passed_count += 1
                    else:
                        status = "WA"
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
                "user_output": user_output[:200] + ("..." if len(user_output) > 200 else ""),
                "expected_output": exp_out[:200] + ("..." if len(exp_out) > 200 else ""),
                "error": err_msg
            })

        final_score = round((passed_count / total_tests) * 10.0, 1)
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
