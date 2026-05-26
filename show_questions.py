# encoding=utf-8
"""
展示上一次做题的所有题目内容。

用法:
    python show_questions.py            # 从默认 JSON 文件读取
    python show_questions.py <file>     # 从指定文件读取
"""
import json
import sys
import io
import os

# 修复 Windows 终端 GBK 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TYPE_NAMES = {
    "single": "单选题",
    "multiple": "多选题",
    "judge": "判断题",
    "fill": "填空客观题",
}

SEPARATOR = "─" * 60


def format_question(q: dict, idx: int):
    """格式化单道题目。"""
    qtype = TYPE_NAMES.get(q.get("type", ""), q.get("type", "未知"))
    lines = []
    lines.append(f"\n{SEPARATOR}")
    lines.append(f"  [{q.get('index', idx+1)}] {qtype}  {q.get('score', '')}")
    lines.append(f"")
    lines.append(f"  {q.get('stem', '(无题干)')}")
    lines.append("")

    if q.get("type") == "fill":
        lines.append(f"  填空数量: {q.get('input_count', 0)}")
    elif q.get("options"):
        for opt in q["options"]:
            lines.append(f"    {opt['label']}. {opt['text']}")

    lines.append("")
    return "\n".join(lines)


def main():
    # 确定文件路径
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # 默认路径
        filepath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "res", "last_questions.json"
        )
        if not os.path.exists(filepath):
            # 尝试从当前目录
            filepath = os.path.join("res", "last_questions.json")

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        print("请先运行 auto_handle.py 完成一次做题，题目会自动保存。")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\n{'='*60}")
    print(f"  上一次做题共 {len(questions)} 道题目")
    print(f"{'='*60}")

    # 按题型分组统计
    type_counts = {}
    for q in questions:
        t = q.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\n  题型分布:")
    for t, c in type_counts.items():
        print(f"    {TYPE_NAMES.get(t, t)}: {c} 题")

    # 打印所有题目
    for i, q in enumerate(questions):
        print(format_question(q, i))

    print(f"{SEPARATOR}")
    print(f"\n  共 {len(questions)} 题")


if __name__ == "__main__":
    main()
