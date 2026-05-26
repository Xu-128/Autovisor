# encoding=utf-8
"""
DeepSeek API 客户端 — 使用 OpenAI 兼容接口，异步包装，JSON 输出。
"""
import json
import time
import asyncio
from openai import OpenAI
from modules.logger import Logger

logger = Logger()

# 单次 API 调用超时（秒）
API_TIMEOUT = 60

QUESTION_PROMPTS = {
    "single": """你是一个大学课程答题助手。用户会提供一道单选题的题干和选项，请选出唯一正确答案。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answer": "选项字母"}

示例：
{"answer": "A"}""",

    "multiple": """你是一个大学课程答题助手。用户会提供一道多选题的题干和选项，请选出所有正确答案。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": ["选项字母1", "选项字母2", ...]}

示例：
{"answers": ["A", "C", "D"]}""",

    "judge": """你是一个大学课程答题助手。用户会提供一道判断题的题干和两个选项（分别代表"对"和"错"）。请判断题目陈述的正确性，选择对应含义的选项字母。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answer": "选项字母"}

示例：
题目：地球是圆的。( ) 选项：A. 对 B. 错 → 输出：{"answer": "A"}
题目：地球是平的。( ) 选项：A. 对 B. 错 → 输出：{"answer": "B"}""",

    "fill": """你是一个大学课程答题助手。用户会提供一道填空题，题干中用 ______ 表示空白处。请按顺序给出每个空的答案。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": ["答案1", "答案2", ...]}

示例：
{"answers": ["1847"]}

注意：答案应简洁准确，只填写关键内容。"""
}

BATCH_QUESTION_PROMPTS = {
    "single": """你是一个大学课程答题助手。下面是一组单选题，请为每道题选出唯一正确答案。
每道题有独立的题号，请在输出中保持题号对应。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": [{"q": 题号, "answer": "选项字母"}, ...]}

正确示例：
{"answers": [{"q": 1, "answer": "A"}, {"q": 3, "answer": "C"}]}""",

    "multiple": """你是一个大学课程答题助手。下面是一组多选题，请为每道题选出所有正确答案。
每道题有独立的题号，请在输出中保持题号对应。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": [{"q": 题号, "answers": ["选项字母1", "选项字母2", ...]}, ...]}

正确示例：
{"answers": [{"q": 1, "answers": ["A", "C"]}, {"q": 2, "answers": ["B", "D"]}]}""",

    "judge": """你是一个大学课程答题助手。下面是一组判断题，每道题有两个选项分别代表"对"和"错"。请判断每道题陈述的正确性，选择对应含义的选项字母。
每道题有独立的题号，请在输出中保持题号对应。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": [{"q": 题号, "answer": "选项字母"}, ...]}

正确示例：
{"answers": [{"q": 1, "answer": "A"}, {"q": 2, "answer": "B"}]}""",

    "fill": """你是一个大学课程答题助手。下面是一组填空题，题干中用 ______ 或空白表示空缺处。请按顺序给出每道题每个空的答案。
每道题有独立的题号，请在输出中保持题号对应。

你必须严格按以下 JSON 格式输出，不要包含任何其他文字：
{"answers": [{"q": 题号, "answers": ["答案1", "答案2", ...]}, ...]}

正确示例：
{"answers": [{"q": 1, "answers": ["1847"]}, {"q": 2, "answers": ["牛顿", "力学"]}]}

注意：答案应简洁准确，只填写关键内容。"""
}


class DeepSeekClient:
    def __init__(self, api_key: str, model: str = "deepseek-v4-flash"):
        if not api_key:
            raise ValueError("DeepSeek API key 未配置，请在 configs.ini [deepseek] 中设置 api_key")
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=API_TIMEOUT,
            max_retries=0,  # 我们自己控制重试
        )

    def _ask_sync(self, question_type: str, question_text: str) -> dict:
        """同步请求 DeepSeek API，返回解析后的 JSON dict。最多重试 3 次。"""
        system_prompt = QUESTION_PROMPTS.get(question_type, QUESTION_PROMPTS["single"])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question_text},
        ]

        last_error = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={'type': 'json_object'},
                    max_tokens=1024,
                )
                content = response.choices[0].message.content
                if not content:
                    logger.debug(f"DeepSeek 返回空内容，第 {attempt+1} 次重试")
                    time.sleep(2)  # 等一会再重试
                    continue
                return json.loads(content)
            except json.JSONDecodeError as e:
                last_error = e
                logger.debug(f"JSON 解析失败，第 {attempt+1} 次重试: {str(e)[:80]}")
                time.sleep(1)
            except Exception as e:
                last_error = e
                logger.debug(f"API 请求失败，第 {attempt+1} 次重试: {logger.summarize_exception(e)}")
                time.sleep(2)

        raise RuntimeError(f"DeepSeek API 请求失败（已重试 3 次）: {last_error}")

    def _ask_batch_sync(self, question_type: str, questions: list[dict]) -> dict:
        """同步批量请求 DeepSeek API，一次发送同类型多道题。"""
        system_prompt = BATCH_QUESTION_PROMPTS.get(question_type, BATCH_QUESTION_PROMPTS["single"])

        parts = []
        for q in questions:
            part = f"---\n题号: {q['index']}\n题目：{q['stem']}"
            if q.get('options'):
                part += "\n选项："
                for opt in q['options']:
                    part += f"\n  {opt['label']}. {opt['text']}"
            if q.get('input_count', 0) > 0:
                part += f"\n共有 {q['input_count']} 个空需要填写。"
            parts.append(part)

        prompt_text = "\n\n".join(parts)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ]

        last_error = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={'type': 'json_object'},
                    max_tokens=4096,
                )
                content = response.choices[0].message.content
                if not content:
                    logger.debug(f"DeepSeek 批量请求返回空内容，第 {attempt+1} 次重试")
                    time.sleep(2)
                    continue
                return json.loads(content)
            except json.JSONDecodeError as e:
                last_error = e
                logger.debug(f"批量 JSON 解析失败，第 {attempt+1} 次重试: {str(e)[:80]}")
                time.sleep(1)
            except Exception as e:
                last_error = e
                logger.debug(f"批量 API 请求失败，第 {attempt+1} 次重试: {logger.summarize_exception(e)}")
                time.sleep(2)

        raise RuntimeError(f"DeepSeek 批量 API 请求失败（已重试 3 次）: {last_error}")

    async def ask(self, question_type: str, question_text: str) -> dict:
        """异步包装，在线程池中执行同步 API 调用，带超时保护。"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._ask_sync, question_type, question_text),
                timeout=API_TIMEOUT + 10  # 略大于内部超时
            )
        except asyncio.TimeoutError:
            raise RuntimeError(f"DeepSeek API 请求超时 ({API_TIMEOUT+10}s)")

    async def ask_batch(self, question_type: str, questions: list[dict]) -> dict:
        """异步批量答题：一次 API 调用处理同类型多道题，带超时保护。"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._ask_batch_sync, question_type, questions),
                timeout=90
            )
        except asyncio.TimeoutError:
            raise RuntimeError("DeepSeek 批量 API 请求超时 (90s)")
