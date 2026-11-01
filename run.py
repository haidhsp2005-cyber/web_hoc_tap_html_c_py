import uvicorn
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(" THEMIS ONLINE JUDGE & EDU PLATFORM")
    print(" Nền tảng học & thi tin học chấm Themis C++, Python, HTML")
    print("=" * 60)
    print("Khởi động máy chủ tại: http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
