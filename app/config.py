import os
import sys
import shutil

IS_VERCEL = bool(os.environ.get("VERCEL"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if IS_VERCEL:
    DATA_DIR = "/tmp/data"
    os.makedirs(DATA_DIR, exist_ok=True)
    DB_PATH = os.path.join(DATA_DIR, "themis_edu.db")
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
    TESTCASE_DIR = os.path.join(DATA_DIR, "testcases")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(TESTCASE_DIR, exist_ok=True)

    # Copy pre-seeded DB from repository to writable /tmp
    repo_db = os.path.join(BASE_DIR, "data", "themis_edu.db")
    if os.path.exists(repo_db) and not os.path.exists(DB_PATH):
        shutil.copy2(repo_db, DB_PATH)
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DB_PATH = os.path.join(DATA_DIR, "themis_edu.db")
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
    TESTCASE_DIR = os.path.join(DATA_DIR, "testcases")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(TESTCASE_DIR, exist_ok=True)

# Compiler & Runtime paths
CPP_COMPILER_DEFAULT = r"C:\Program Files\CodeBlocks\MinGW\bin\g++.exe"
if os.path.exists(CPP_COMPILER_DEFAULT):
    CPP_COMPILER = CPP_COMPILER_DEFAULT
else:
    CPP_COMPILER = "g++"

PYTHON_EXECUTABLE = sys.executable

# Standard judging parameters
DEFAULT_TIME_LIMIT_MS = 1000
DEFAULT_MEMORY_LIMIT_MB = 256
MAX_PROBLEM_SCORE = 10.0
