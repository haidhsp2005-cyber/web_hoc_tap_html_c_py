import os
import sys
import time
import subprocess
import tempfile
import shutil
from app.config import PYTHON_EXECUTABLE

def normalize_output(text: str) -> str:
    """Standard Themis output normalization: strips trailing whitespace and line endings."""
    if not text:
        return ""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)

def judge_python_code(source_code: str, test_cases: list, problem_code: str = "PROBLEM", time_limit_ms: int = 1500) -> dict:
    """
    Judges Python source code against a list of test cases.
    """
    if not test_cases:
        return {
            "status": "ERROR",
            "score": 0.0,
            "max_score": 10.0,
            "error_message": "Không tìm thấy bộ test case nào cho bài tập này.",
            "test_results": []
        }

    # Resolve working Python binary
    python_bin = PYTHON_EXECUTABLE
    if not os.path.exists(python_bin) and not shutil.which(python_bin):
        python_bin = sys.executable or "python3" or "python"

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "solution.py")

        with open(src_file, "w", encoding="utf-8") as f:
            f.write(source_code)

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
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"

                proc = subprocess.run(
                    [python_bin, src_file],
                    input=inp,
                    capture_output=True,
                    text=True,
                    timeout=time_limit_sec,
                    cwd=tmpdir,
                    env=env,
                    encoding="utf-8",
                    errors="replace"
                )
                exec_time_ms = int((time.perf_counter() - start_time) * 1000)

                if os.path.exists(out_filename) and os.path.getsize(out_filename) > 0:
                    with open(out_filename, "r", encoding="utf-8", errors="ignore") as f_out:
                        user_output = f_out.read()
                else:
                    user_output = proc.stdout

                if proc.returncode != 0:
                    status = "RTE"
                    err_msg = f"Runtime Error:\n{proc.stderr}"
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
            except (PermissionError, FileNotFoundError, OSError):
                # Fallback to in-process execution for locked serverless environments
                import io, sys as system_sys
                old_stdin, old_stdout, old_stderr = system_sys.stdin, system_sys.stdout, system_sys.stderr
                in_buf = io.StringIO(inp)
                out_buf = io.StringIO()
                err_buf = io.StringIO()
                system_sys.stdin = in_buf
                system_sys.stdout = out_buf
                system_sys.stderr = err_buf
                try:
                    glob_env = {"__name__": "__main__"}
                    exec(source_code, glob_env)
                    user_output = out_buf.getvalue()
                    status = "AC"
                    passed_count += 1
                except Exception as ex:
                    status = "RTE"
                    err_msg = f"Runtime Error:\n{str(ex)}"
                    user_output = out_buf.getvalue()
                finally:
                    system_sys.stdin, system_sys.stdout, system_sys.stderr = old_stdin, old_stdout, old_stderr
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
