import os
import re
import zipfile
import shutil

def parse_themis_zip(zip_path: str, extract_to_dir: str = None) -> list:
    """
    Parses a Themis-formatted ZIP file containing test cases.
    Returns a list of dicts:
    [
        {"test_number": 1, "input_data": "...", "expected_output": "..."},
        ...
    ]
    Supports:
    1. Folders: Test01/BAI1.INP, Test01/BAI1.OUT (or .ans)
    2. Folders: 1/inp, 1/out
    3. Flat files: test01.inp, test01.out, or 01.inp, 01.out
    """
    test_cases = []
    
    if not zipfile.is_zipfile(zip_path):
        raise ValueError("File tải lên không phải là file ZIP hợp lệ.")

    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = zf.namelist()
        
        # Structure 1: Subfolders grouped by test (e.g. Test01/, Test02/, or 1/, 2/)
        folder_groups = {}
        flat_files = {}

        for filename in file_list:
            if filename.endswith("/") or filename.endswith("\\"):
                continue  # skip directory entries
            
            clean_name = filename.replace("\\", "/")
            parts = clean_name.split("/")
            
            if len(parts) >= 2:
                folder_name = parts[-2]
                base_file = parts[-1]
                if folder_name not in folder_groups:
                    folder_groups[folder_name] = []
                folder_groups[folder_name].append((clean_name, base_file))
            else:
                flat_files[parts[0]] = clean_name

        # Process folder groups (e.g., Test01, Test02...)
        if folder_groups:
            # Sort folders naturally (Test1, Test2, ... Test10)
            def natural_sort_key(s):
                return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
            sorted_folders = sorted(folder_groups.keys(), key=natural_sort_key)
            
            test_idx = 1
            for folder in sorted_folders:
                files = folder_groups[folder]
                inp_content = None
                out_content = None
                
                for full_path, file_name in files:
                    lower_name = file_name.lower()
                    if lower_name.endswith(".inp") or lower_name.endswith(".in") or "input" in lower_name:
                        try:
                            inp_content = zf.read(full_path).decode("utf-8")
                        except UnicodeDecodeError:
                            inp_content = zf.read(full_path).decode("latin-1")
                    elif lower_name.endswith(".out") or lower_name.endswith(".ans") or "output" in lower_name:
                        try:
                            out_content = zf.read(full_path).decode("utf-8")
                        except UnicodeDecodeError:
                            out_content = zf.read(full_path).decode("latin-1")
                
                if inp_content is not None and out_content is not None:
                    test_cases.append({
                        "test_number": test_idx,
                        "folder_name": folder,
                        "input_data": inp_content,
                        "expected_output": out_content
                    })
                    test_idx += 1

        # Fallback to flat files if no folder groups matched
        if not test_cases and flat_files:
            # Group by file name prefix
            inp_files = {}
            out_files = {}
            for name, full_path in flat_files.items():
                lower = name.lower()
                prefix = re.sub(r'\.(inp|in|out|ans)$', '', lower)
                if lower.endswith(('.inp', '.in')):
                    try:
                        inp_files[prefix] = zf.read(full_path).decode('utf-8')
                    except UnicodeDecodeError:
                        inp_files[prefix] = zf.read(full_path).decode('latin-1')
                elif lower.endswith(('.out', '.ans')):
                    try:
                        out_files[prefix] = zf.read(full_path).decode('utf-8')
                    except UnicodeDecodeError:
                        out_files[prefix] = zf.read(full_path).decode('latin-1')
            
            matched_keys = sorted(set(inp_files.keys()).intersection(set(out_files.keys())))
            for i, k in enumerate(matched_keys, 1):
                test_cases.append({
                    "test_number": i,
                    "folder_name": f"Test{i:02d}",
                    "input_data": inp_files[k],
                    "expected_output": out_files[k]
                })

    return test_cases
