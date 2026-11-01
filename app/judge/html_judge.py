import html.parser
import re

SELF_CLOSING_TAGS = {'br', 'hr', 'img', 'input', 'link', 'meta', 'base', 'area', 'col', 'embed', 'param', 'source', 'track', 'wbr'}

class HTMLLineValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []  # list of (tag, (line, col))
        self.errors = []
        self.warnings = []
        self.tags_found = []

    def handle_starttag(self, tag, attrs):
        pos = self.getpos()
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}
        
        self.tags_found.append({
            "tag": tag_lower,
            "attrs": attr_dict,
            "line": pos[0],
            "col": pos[1]
        })

        # Check common tag attribute requirements
        if tag_lower == 'img':
            if 'src' not in attr_dict or not attr_dict['src']:
                self.warnings.append({
                    "line": pos[0],
                    "col": pos[1],
                    "type": "missing_attr",
                    "message": f"Dòng {pos[0]}: Thẻ <img> nên có thuộc tính 'src' để hiển thị hình ảnh."
                })
            if 'alt' not in attr_dict:
                self.warnings.append({
                    "line": pos[0],
                    "col": pos[1],
                    "type": "missing_attr",
                    "message": f"Dòng {pos[0]}: Thẻ <img> thiếu thuộc tính 'alt' (mô tả hình ảnh hỗ trợ SEO & tiếp cận)."
                })

        if tag_lower == 'a':
            if 'href' not in attr_dict:
                self.warnings.append({
                    "line": pos[0],
                    "col": pos[1],
                    "type": "missing_attr",
                    "message": f"Dòng {pos[0]}: Thẻ <a> thiếu thuộc tính 'href' để chỉ định liên kết."
                })

        if tag_lower not in SELF_CLOSING_TAGS:
            self.stack.append((tag_lower, pos))

    def handle_endtag(self, tag):
        pos = self.getpos()
        tag_lower = tag.lower()

        if tag_lower in SELF_CLOSING_TAGS:
            self.warnings.append({
                "line": pos[0],
                "col": pos[1],
                "type": "redundant_close",
                "message": f"Dòng {pos[0]}: Thẻ <{tag_lower}> là thẻ tự đóng, không cần viết thẻ đóng </{tag_lower}>."
            })
            return

        if not self.stack:
            self.errors.append({
                "line": pos[0],
                "col": pos[1],
                "type": "unexpected_close",
                "message": f"Dòng {pos[0]}, Cột {pos[1]}: Thẻ đóng </{tag_lower}> bị thừa (không có thẻ mở tương ứng)."
            })
            return

        last_tag, last_pos = self.stack.pop()
        if last_tag != tag_lower:
            self.errors.append({
                "line": pos[0],
                "col": pos[1],
                "type": "mismatched_tag",
                "message": f"Dòng {pos[0]}, Cột {pos[1]}: Đóng thẻ </{tag_lower}> sai vị trí! Thẻ mở gần nhất là <{last_tag}> ở dòng {last_pos[0]}."
            })

    def validate_complete(self):
        # Any remaining unclosed tags
        for tag, pos in reversed(self.stack):
            self.errors.append({
                "line": pos[0],
                "col": pos[1],
                "type": "unclosed_tag",
                "message": f"Dòng {pos[0]}, Cột {pos[1]}: Thẻ <{tag}> chưa được đóng!"
            })


def judge_html_code(html_code: str, criteria: list = None) -> dict:
    """
    Judges HTML code submitted by a student.
    Returns:
    {
        "status": "AC" or "WA",
        "score": 10.0,
        "syntax_errors": [...],
        "syntax_warnings": [...],
        "criteria_results": [...],
        "summary": "..."
    }
    """
    validator = HTMLLineValidator()
    try:
        validator.feed(html_code)
        validator.close()
        validator.validate_complete()
    except Exception as e:
        validator.errors.append({
            "line": 1,
            "col": 1,
            "type": "parse_fatal",
            "message": f"Lỗi cú pháp phân tích HTML: {str(e)}"
        })

    # Criteria evaluation
    criteria_results = []
    total_criteria_points = 0.0
    earned_criteria_points = 0.0

    if not criteria:
        # Default criteria if none configured
        criteria = [
            {"id": "c1", "name": "Cấu trúc chuẩn HTML", "description": "Có thẻ <html>, <head>, <body>", "points": 3.0, "type": "basic_structure"},
            {"id": "c2", "name": "Tiêu đề trang hoặc đề mục", "description": "Có thẻ tiêu đề <title> hoặc <h1>-<h6>", "points": 3.0, "type": "headings"},
            {"id": "c3", "name": "Nội dung văn bản", "description": "Có ít nhất 1 đoạn văn <p> hoặc danh sách", "points": 4.0, "type": "content"}
        ]

    lower_code = html_code.lower()

    for c in criteria:
        c_type = c.get("type", "custom")
        c_name = c.get("name", "Tiêu chí")
        c_desc = c.get("description", "")
        max_pts = float(c.get("points", 2.0))
        total_criteria_points += max_pts
        passed = False
        message = ""

        if c_type == "basic_structure":
            has_html = "<html" in lower_code
            has_body = "<body" in lower_code
            if has_html and has_body:
                passed = True
                message = "Đã có đầy đủ cấu trúc <html> và <body> chuẩn."
            else:
                passed = False
                message = "Thiếu thẻ <html> hoặc <body>."

        elif c_type == "headings":
            headings = [t["tag"] for t in validator.tags_found if t["tag"] in ["h1", "h2", "h3", "h4", "h5", "h6", "title"]]
            if headings:
                passed = True
                message = f"Tìm thấy {len(headings)} thẻ tiêu đề: {', '.join(set(headings))}."
            else:
                passed = False
                message = "Chưa có thẻ tiêu đề nào (như <h1>, <h2> hoặc <title>)."

        elif c_type == "content":
            has_p = any(t["tag"] == "p" for t in validator.tags_found)
            has_list = any(t["tag"] in ["ul", "ol", "li"] for t in validator.tags_found)
            if has_p or has_list:
                passed = True
                message = "Có các thẻ đoạn văn hoặc danh sách nội dung."
            else:
                passed = False
                message = "Chưa có thẻ đoạn văn <p> hoặc danh sách <ul>/<ol>."

        elif c_type == "table":
            has_table = any(t["tag"] == "table" for t in validator.tags_found)
            tr_count = sum(1 for t in validator.tags_found if t["tag"] == "tr")
            td_count = sum(1 for t in validator.tags_found if t["tag"] in ["td", "th"])
            if has_table and tr_count >= 1 and td_count >= 1:
                passed = True
                message = f"Bảng <table> hợp lệ với {tr_count} dòng và {td_count} ô dữ liệu."
            else:
                passed = False
                message = "Yêu cầu có thẻ <table> chứa ít nhất 1 hàng <tr> và các ô <td>/<th>."

        elif c_type == "contains_tag":
            req_tag = c.get("tag", "").lower()
            if any(t["tag"] == req_tag for t in validator.tags_found):
                passed = True
                message = f"Đã tìm thấy thẻ <{req_tag}> theo yêu cầu."
            else:
                passed = False
                message = f"Chưa tìm thấy thẻ <{req_tag}> theo yêu cầu đề bài."

        elif c_type == "contains_text":
            expected_text = c.get("text", "")
            if expected_text.lower() in lower_code:
                passed = True
                message = f"Nội dung chứa đoạn chữ yêu cầu: '{expected_text}'."
            else:
                passed = False
                message = f"Không tìm thấy đoạn chữ '{expected_text}' trong mã HTML."

        else:
            # Custom keyword match
            kw = c.get("keyword", "")
            if kw and kw.lower() in lower_code:
                passed = True
                message = f"Đáp ứng tiêu chí '{kw}'."
            else:
                passed = False
                message = f"Chưa đáp ứng tiêu chí: {c_desc}"

        score_this = max_pts if passed else 0.0
        earned_criteria_points += score_this

        criteria_results.append({
            "name": c_name,
            "description": c_desc,
            "max_points": max_pts,
            "earned_points": score_this,
            "passed": passed,
            "feedback": message
        })

    # Scoring algorithm out of 10.0 points
    # If there are syntax errors, deduct proportional points
    syntax_error_count = len(validator.errors)
    syntax_penalty = min(syntax_error_count * 2.0, 5.0)  # max penalty 5.0

    raw_score = (earned_criteria_points / total_criteria_points * 10.0) if total_criteria_points > 0 else 10.0
    final_score = max(0.0, round(raw_score - syntax_penalty, 1))

    status = "AC" if (final_score >= 10.0 and syntax_error_count == 0) else ("WA" if final_score < 5.0 else "PARTIAL")

    return {
        "status": status,
        "score": final_score,
        "max_score": 10.0,
        "syntax_errors": validator.errors,
        "syntax_warnings": validator.warnings,
        "criteria_results": criteria_results,
        "summary": f"Điểm đạt: {final_score}/10.0. " + (
            "Chúc mừng! Bài làm hoàn hảo không lỗi cú pháp!" if status == "AC" else 
            f"Phát hiện {syntax_error_count} lỗi cú pháp cần sửa theo số dòng thông báo bên dưới."
        )
    }
