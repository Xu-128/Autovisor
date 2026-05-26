# encoding=utf-8
"""
让 DeepSeek 回答上一次保存的题目，并统计每题用时。

用法:
    python ds_test.py                  # 使用默认 JSON 和默认配置
    python ds_test.py <json文件>       # 指定题目文件
"""
import json
import sys
import io
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from modules.deepseek_client import DeepSeekClient
from modules.configs import Config

TYPE_NAMES = {
    "single": "单选题",
    "multiple": "多选题",
    "judge": "判断题",
    "fill": "填空客观题",
}

SEP = "─" * 60


def build_prompt(q: dict) -> str:
    """构建发给 DeepSeek 的提示文本。"""
    qtype = q.get("type", "single")
    lines = [f"题目：{q.get('stem', '')}"]

    if qtype == "fill":
        lines.append(f"共有 {q.get('input_count', 0)} 个空需要填写。")
    elif q.get("options"):
        lines.append("选项：")
        for opt in q["options"]:
            lines.append(f"  {opt['label']}. {opt['text']}")
        if qtype == "single":
            lines.append("\n请选出唯一正确答案。")
        elif qtype == "multiple":
            lines.append("\n请选出所有正确答案（可多选）。")
        elif qtype == "judge":
            lines.append("\n请判断正误（A=错, B=对）。")

    return "\n".join(lines)


def main():
    # 读取题目
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = os.path.join("res", "last_questions.json")

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        print("请先运行 auto_handle.py 完成一次做题。")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\n{'='*60}")
    print(f"  共 {len(questions)} 道题目")
    print(f"{'='*60}\n")

    # 初始化 DeepSeek
    config = Config("configs.ini")
    if not config.deepseek_api_key:
        print("未配置 DeepSeek API Key")
        return

    client = DeepSeekClient(
        api_key=config.deepseek_api_key,
        model=config.deepseek_model,
    )
    print(f"模型: {config.deepseek_model}\n")

    total_time = 0.0
    success = 0

    for i, q in enumerate(questions):
        qtype = q.get("type", "single")
        type_name = TYPE_NAMES.get(qtype, qtype)
        idx = q.get("index", i + 1)

        print(f"{SEP}")
        print(f"  [{idx}] {type_name}  {q.get('score', '')}")
        print(f"  {q.get('stem', '(无)')}")
        if qtype != "fill" and q.get("options"):
            for opt in q["options"]:
                print(f"    {opt['label']}. {opt['text']}")
        print()

        # 调用 DeepSeek 并计时
        prompt = build_prompt(q)
        t0 = time.time()
        try:
            result = client._ask_sync(qtype, prompt)
            elapsed = time.time() - t0
            total_time += elapsed
            success += 1

            # 格式化答案
            if "answers" in result:
                ans_str = ", ".join(result["answers"])
            elif "answer" in result:
                ans_str = result["answer"]
            else:
                ans_str = str(result)

            print(f"  -> {ans_str}")
            print(f"  ⏱  {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  -> 失败: {e}")
            print(f"  ⏱  {elapsed:.1f}s (超时)")
        print()

    print(f"{SEP}")
    avg = total_time / success if success > 0 else 0
    print(f"  成功: {success}/{len(questions)}  总耗时: {total_time:.1f}s  平均: {avg:.1f}s/题")
    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
