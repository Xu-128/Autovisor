# encoding=utf-8
"""
作业答题引擎 — 题目提取、题型检测、答案提交、页面导航。
"""
import re
import json
import time
from dataclasses import dataclass, asdict, field
from enum import Enum
from playwright.async_api import Page, Locator, TimeoutError as PlTimeoutError

from modules.logger import Logger
from modules.deepseek_client import DeepSeekClient
from modules.progress import show_progress

logger = Logger()


class QuestionType(Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"
    JUDGE = "judge"
    FILL = "fill"


@dataclass
class Question:
    index: int
    type: QuestionType
    stem: str
    options: list = field(default_factory=list)
    input_count: int = 0
    score: str = ""
    answer: str = ""  # DeepSeek 返回的答案


async def get_total_question_count(page: Page) -> int:
    """从右侧答题卡获取题目总数。"""
    await page.wait_for_timeout(1000)

    # 多策略查找答题卡题号按钮
    selectors = [
        ".grid button",
        "[class*=grid] button",
        ".grid-cols-7 button",
        "button.size-\\[44px\\]",
        # 宽泛匹配: 答题卡区域内所有 button
        ".col-span-4 button",
    ]

    for selector in selectors:
        try:
            card_btns = page.locator(selector)
            count = await card_btns.count()
            numeric_count = 0
            for i in range(count):
                try:
                    text = (await card_btns.nth(i).text_content() or "").strip()
                    if text.isdigit():
                        numeric_count += 1
                except Exception:
                    continue
            if numeric_count > 0:
                return numeric_count
        except Exception:
            continue

    # 最终回退: 找所有 button，筛选纯数字文本的
    try:
        all_btns = page.locator("button")
        count = await all_btns.count()
        numeric_count = 0
        for i in range(count):
            try:
                text = (await all_btns.nth(i).text_content() or "").strip()
                if text.isdigit() and 1 <= int(text) <= 100:
                    numeric_count += 1
            except Exception:
                continue
        if numeric_count > 0:
            return numeric_count
    except Exception:
        pass

    return 0


async def parse_current_question(page: Page) -> Question | None:
    """解析当前页面中可见的一道题。"""
    await page.wait_for_timeout(500)

    # 快速检查题目区是否存在（避免 text_content 用 24h 超时死等）
    q_area = page.locator(".question-area-content")
    if await q_area.count() == 0:
        logger.debug("  [解析] .question-area-content 不存在，跳过")
        return None

    # 在 .question-area-content 内找题号 — 不同题型可能用不同 font class
    number_selectors = [
        "span.font-AP-65.text-mainText",
        "span.font-AP-60.text-mainText",
        "span.font-AP-55.text-mainText",
        "span.text-mainText",  # 兜底：任何 font 的 text-mainText
    ]
    number_el = None
    for sel in number_selectors:
        el = q_area.locator(sel).first
        if await el.count() > 0:
            number_el = el
            break

    if number_el is None:
        # 诊断：打印 .question-area-content 内所有 span 的 class，帮助排查
        try:
            all_spans = q_area.locator("span")
            span_count = await all_spans.count()
            classes_found = []
            for si in range(min(span_count, 20)):
                try:
                    cls = await all_spans.nth(si).get_attribute("class")
                    txt = (await all_spans.nth(si).text_content() or "")[:30]
                    if cls:
                        classes_found.append(f"'{txt}' [{cls}]")
                except Exception:
                    pass
            logger.debug(f"  [解析] 题号元素未匹配, 页面 span: {', '.join(classes_found)}")
        except Exception:
            pass
        logger.debug("  [解析] 题号元素不存在（已尝试全部备选选择器），跳过")
        return None
    try:
        number_text = await number_el.text_content(timeout=3000)
        q_index = int(re.search(r'(\d+)', number_text or "1").group(1))
    except Exception:
        q_index = 1

    # 检测题型 — 通过彩色 badge
    q_type = None
    type_el = None
    # 按优先级尝试每种 badge
    for selector, qtype_enum in [
        ("span.text-green", QuestionType.SINGLE),
        ("span.text-magenta", QuestionType.MULTIPLE),
        ("span.text-pink", QuestionType.JUDGE),
    ]:
        el = page.locator(f".question-area-content {selector}")
        if await el.count() > 0:
            q_type = qtype_enum
            type_el = el.first
            break

    if q_type is None:
        # 试试填空（橙色 badge）
        fill_el = page.locator(".question-area-content span:has-text('填空客观题')")
        if await fill_el.count() > 0:
            q_type = QuestionType.FILL
            type_el = fill_el.first

    if q_type is None:
        logger.debug(f"第{q_index}题: 无法识别题型, 跳过")
        return None

    # 提取分值
    score = ""
    try:
        score_el = page.locator(".question-area-content small").first
        raw = await score_el.text_content() or ""
        raw = raw.strip()
        # 去掉可能已经有的括号，只保留数字 + "分"
        m = re.search(r'(\d+)\s*分', raw)
        if m:
            score = m.group(1) + "分"
    except Exception:
        pass

    # 提取题干: font-AP-55 text-[24px]（section header 用的是 font-AP-65，要避开）
    stem = ""
    try:
        stem_els = page.locator(".question-area-content .font-AP-55.text-\\[24px\\]")
        if await stem_els.count() > 0:
            stem = await stem_els.first.inner_text()
            stem = stem.strip()
    except Exception:
        pass

    # 提取选项或输入框
    options = []
    input_count = 0

    if q_type == QuestionType.FILL:
        inputs = page.locator(".question-area-content input[type='text']")
        input_count = await inputs.count()
    else:
        # 找到选项容器内的所有 label
        labels = page.locator(".question-area-content label")
        label_count = await labels.count()
        for j in range(label_count):
            try:
                label = labels.nth(j)
                # 提取字母
                badge_div = label.locator("div.notranslate").first
                letter = ""
                try:
                    letter = (await badge_div.text_content() or "").strip()
                except Exception:
                    # 可能没有 notranslate class，直接取第一个 div 的文本
                    first_div = label.locator("div").first
                    letter = (await first_div.text_content() or "").strip()

                # 提取选项文本
                option_text = ""
                try:
                    span = label.locator("span").first
                    option_text = (await span.text_content() or "").strip()
                except Exception:
                    pass

                if letter and option_text:
                    options.append({"label": letter, "text": option_text})
            except Exception:
                continue

    return Question(
        index=q_index,
        type=q_type,
        stem=stem,
        options=options,
        input_count=input_count,
        score=score,
    )


async def answer_current_question(page: Page, question: Question, client: DeepSeekClient) -> dict | None:
    """回答当前显示的一道题，返回 DeepSeek 的答案 dict（失败返回 None）。"""
    type_name = {
        QuestionType.SINGLE: "单选题",
        QuestionType.MULTIPLE: "多选题",
        QuestionType.JUDGE: "判断题",
        QuestionType.FILL: "填空客观题",
    }.get(question.type, "未知")

    logger.info(f"  [{question.index}] {type_name} ({question.score})")

    try:
        prompt_text = _build_prompt(question)
        result = await client.ask(question.type.value, prompt_text)

        if question.type == QuestionType.FILL:
            await _do_fill(page, result)
        else:
            await _do_select(page, question.type, result)

        return result
    except Exception as e:
        logger.log_exception(f"  第{question.index}题作答失败", e)
        return None


def _build_prompt(q: Question) -> str:
    lines = [f"题目：{q.stem}"]
    if q.type == QuestionType.FILL:
        lines.append(f"共有 {q.input_count} 个空需要填写。")
    elif q.options:
        lines.append("选项：")
        for opt in q.options:
            lines.append(f"  {opt['label']}. {opt['text']}")
        if q.type == QuestionType.SINGLE:
            lines.append("\n请选出唯一正确答案。")
        elif q.type == QuestionType.MULTIPLE:
            lines.append("\n请选出所有正确答案（可多选）。")
        elif q.type == QuestionType.JUDGE:
            lines.append("\n请根据题目陈述的正确与否，选出代表对应含义的选项。")
    return "\n".join(lines)


def print_question(q: Question):
    """将题目内容打印到终端，用户可检查识别是否正确。"""
    type_name = {
        QuestionType.SINGLE: "单选题",
        QuestionType.MULTIPLE: "多选题",
        QuestionType.JUDGE: "判断题",
        QuestionType.FILL: "填空客观题",
    }.get(q.type, "未知")

    print(f"\n  ┌─ [{q.index}] {type_name}  {q.score}", flush=True)
    print(f"  │ {q.stem}", flush=True)
    if q.type == QuestionType.FILL:
        print(f"  │ 填空数: {q.input_count}", flush=True)
    elif q.options:
        for opt in q.options:
            print(f"  │   {opt['label']}. {opt['text']}", flush=True)
    print(f"  └{'─'*40}", flush=True)


def _format_answer(result: dict) -> str:
    """将 DeepSeek 返回的答案格式化为可读字符串。"""
    if "answers" in result:
        return ", ".join(result["answers"])
    if "answer" in result:
        return result["answer"]
    return str(result)


async def _do_select(page: Page, q_type: QuestionType, result: dict):
    """点击选项 label。"""
    if q_type == QuestionType.MULTIPLE:
        answers = result.get("answers", [])
        if not answers and "answer" in result:
            answers = [result["answer"]]
    else:
        answer = result.get("answer", "")
        answers = [answer] if answer else []

    if not answers:
        logger.warn("  DeepSeek 未返回有效答案")
        return

    labels = page.locator(".question-area-content label")
    for ans in answers:
        ans = ans.strip().upper()
        matched = False
        label_count = await labels.count()
        for i in range(label_count):
            try:
                label = labels.nth(i)
                badge = label.locator("div.notranslate").first
                letter = (await badge.text_content() or "").strip().upper()
                if letter == ans:
                    await label.click(timeout=3000)
                    await page.wait_for_timeout(300)
                    matched = True
                    break
            except Exception:
                continue

        if not matched:
            # 回退: 点 label 本身的第一个 div
            try:
                await labels.first.locator("div").first.click(timeout=3000)
                await page.wait_for_timeout(300)
            except Exception:
                pass


async def _do_fill(page: Page, result: dict):
    """填写填空输入框。"""
    answers = result.get("answers", [])
    if not answers and "answer" in result:
        answers = [result["answer"]]

    if not answers:
        logger.warn("  DeepSeek 未返回有效填空答案")
        return

    inputs = page.locator(".question-area-content input[type='text']")
    input_count = await inputs.count()
    for i, ans in enumerate(answers):
        if i >= input_count:
            break
        try:
            await inputs.nth(i).fill(str(ans), timeout=3000)
        except Exception as e:
            logger.debug(f"  填写第{i+1}个空失败: {logger.summarize_exception(e)}")


async def click_next_button(page: Page) -> str:
    """
    点击底部导航区的"下一题"按钮。
    返回按钮文本: "next"=还有下一题, "submit"=已是最后一题, "none"=未找到按钮
    """
    # 底部按钮区在 .question-area-content 后面的 div 里
    nav_area = page.locator(".question-area-content + div button, .question-area-content ~ div button")
    count = await nav_area.count()
    logger.debug(f"  [按钮] nav_area 匹配到 {count} 个按钮")
    if count < 2:
        return "none"

    next_btn = nav_area.last  # 右边的是"下一题"/"提交"

    try:
        text = (await next_btn.text_content() or "").strip()
    except Exception:
        return "none"

    logger.debug(f"  [按钮] last 按钮文本: '{text}'")

    if "提交" in text:
        return "submit"

    t_click = time.time()
    try:
        await next_btn.click(timeout=5000)
        elapsed = time.time() - t_click
        logger.debug(f"  [按钮] 点击'{text}'完成, 耗时 {elapsed:.1f}s")
        await page.wait_for_timeout(800)
        return "next"
    except Exception as e:
        elapsed = time.time() - t_click
        logger.debug(f"  [按钮] 点击'{text}'失败/超时 ({elapsed:.1f}s): {logger.summarize_exception(e)}")
        return "none"


async def click_answer_card_button(page: Page, question_number: int) -> bool:
    """点击答题卡中指定题号的按钮来跳转题目。"""
    logger.debug(f"  [答题卡] 尝试跳转到第{question_number}题")
    await page.wait_for_timeout(300)
    selectors = [
        ".grid button",
        "[class*=grid] button",
        ".grid-cols-7 button",
        "button.size-\\[44px\\]",
        ".col-span-4 button",
    ]

    for selector in selectors:
        try:
            card_btns = page.locator(selector)
            count = await card_btns.count()
            for i in range(count):
                try:
                    btn = card_btns.nth(i)
                    text = (await btn.text_content() or "").strip()
                    if text == str(question_number):
                        await btn.click(timeout=3000)
                        await page.wait_for_timeout(800)
                        logger.debug(f"  [答题卡] 跳转到第{question_number}题成功 (selector: {selector})")
                        return True
                except Exception:
                    continue
        except Exception:
            continue

    logger.debug(f"  [答题卡] 未找到第{question_number}题的按钮")
    return False


async def answer_all_questions(page: Page, client: DeepSeekClient) -> int:
    """
    两趟式作答：
    Pass 1 — 逐题遍历，解析题干和选项，收集所有题目。
    Pass 2 — 按题型分组，每组一次批量 API 调用，然后逐题点击答案。
    """
    total = await get_total_question_count(page)
    if total == 0:
        logger.warn("未检测到任何题目（答题卡为空）")
        return 0

    logger.info(f"共 {total} 道题，开始逐题解析...")

    # 强制从第 1 题开始
    await click_answer_card_button(page, 1)
    await page.wait_for_timeout(500)

    # ==================== Pass 1: 收集所有题目 ====================
    all_questions = []

    for i in range(total):
        t_q_start = time.time()

        q = await parse_current_question(page)
        if q is None:
            logger.warn(f"  第{i+1}道题解析失败, 跳过")
            if i < total - 1:
                await _navigate_forward(page, q_index=i + 1)
            continue

        q.index = i + 1
        all_questions.append(q)
        print_question(q)

        t_elapsed = time.time() - t_q_start
        logger.debug(f"  [解析] 第{i+1}题 ({q.type.value}) 解析完成, 耗时 {t_elapsed:.1f}s")

        show_progress("解析进度:", i + 1, total)

        if i < total - 1:
            moved = await _navigate_forward(page, q_index=q.index)
            if not moved:
                break

    if not all_questions:
        logger.warn("未能解析任何题目")
        return 0

    # ==================== 按题型分组，批量调用 API ====================
    groups = {}
    for q in all_questions:
        if q.type not in groups:
            groups[q.type] = []
        groups[q.type].append(q)

    type_label = {
        QuestionType.SINGLE: "单选题",
        QuestionType.MULTIPLE: "多选题",
        QuestionType.JUDGE: "判断题",
        QuestionType.FILL: "填空客观题",
    }

    answer_map = {}  # q.index → answer dict from API

    for q_type, group in groups.items():
        label = type_label.get(q_type, "未知")
        logger.info(f"批量处理 {len(group)} 道{label}...")

        q_data = []
        for q in group:
            data = {"index": q.index, "stem": q.stem}
            if q.options:
                data["options"] = q.options
            if q.input_count > 0:
                data["input_count"] = q.input_count
            q_data.append(data)

        try:
            result = await client.ask_batch(q_type.value, q_data)
            items = result.get("answers", [])
            for item in items:
                idx = item.get("q")
                if idx:
                    answer_map[idx] = item
            logger.info(f"  {label}批量作答完成: {len(items)} 题")
        except Exception as e:
            logger.log_exception(f"  {label}批量作答失败", e)

    # 回填答案到 Question 对象
    for q in all_questions:
        if q.index in answer_map:
            q.answer = _format_answer(answer_map[q.index])

    # ==================== Pass 2: 回到第 1 题，逐题点击答案 ====================
    await click_answer_card_button(page, 1)
    await page.wait_for_timeout(500)

    answered = 0
    for i, q in enumerate(all_questions):
        t_apply = time.time()

        await page.wait_for_timeout(300)

        if q.index in answer_map:
            try:
                result = answer_map[q.index]
                if q.type == QuestionType.FILL:
                    await _do_fill(page, result)
                else:
                    await _do_select(page, q.type, result)
                answered += 1
                print(f"    -> DS: {q.answer}", flush=True)
            except Exception as e:
                logger.log_exception(f"  第{q.index}题作答失败", e)
        else:
            print(f"    -> 无答案", flush=True)

        logger.debug(f"  [作答] 第{q.index}题 应用完成, 耗时 {time.time() - t_apply:.1f}s")

        show_progress("作答进度:", i + 1, len(all_questions),
                      suffix=f"{answered}/{len(all_questions)}")

        if i < len(all_questions) - 1:
            moved = await _navigate_forward(page, q_index=q.index)
            if not moved:
                break

    print(flush=True)
    logger.info(f"作答完成: {answered}/{len(all_questions)} 题回答成功")
    save_questions_json(all_questions)
    return answered


def save_questions_json(questions: list[Question], filepath: str = None):
    """将题目列表保存为 JSON 文件。"""
    if filepath is None:
        filepath = "res/last_questions.json"

    data = []
    for q in questions:
        item = {
            "index": q.index,
            "type": q.type.value,
            "stem": q.stem,
            "score": q.score,
            "answer": q.answer,
        }
        if q.type == QuestionType.FILL:
            item["input_count"] = q.input_count
        else:
            item["options"] = q.options
        data.append(item)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"题目已保存到 {filepath}")
    except Exception as e:
        logger.debug(f"保存题目失败: {logger.summarize_exception(e)}")


async def _navigate_forward(page: Page, q_index: int) -> bool:
    """从当前题移到下一题。返回 True=成功移动，False=已是最后一题。"""
    t0 = time.time()
    btn_text = await click_next_button(page)
    if btn_text == "submit":
        logger.info("  检测到'提交'按钮，已是最后一题")
        return False
    if btn_text == "none":
        logger.debug(f"  [导航] click_next_button 返回 none，回退到答题卡跳转")
        ok = await click_answer_card_button(page, q_index + 1)
        if not ok:
            logger.debug(f"  [导航] 答题卡跳转到第{q_index + 1}题也失败")
            return False

    # 轮询等待新题号出现（页面渲染可能很慢，反复检查直到就绪）
    next_num = q_index + 1
    max_wait = 60
    while True:
        try:
            await page.wait_for_function(
                f"""() => {{
                    const el = document.querySelector('.question-area-content span.text-mainText');
                    if (!el) return false;
                    const m = el.textContent.match(/\\d+/);
                    return m && parseInt(m[0]) === {next_num};
                }}""",
                timeout=5000
            )
            elapsed = time.time() - t0
            logger.debug(f"  [导航] {q_index}→{next_num} 完成, 耗时 {elapsed:.1f}s")
            break
        except Exception:
            elapsed = time.time() - t0
            if elapsed > max_wait:
                logger.warn(f"  [导航] {q_index}→{next_num} 等待 {max_wait}s 仍未就绪，强制继续")
                break
            logger.debug(f"  [导航] {q_index}→{next_num} 页面未就绪, 已等 {elapsed:.1f}s, 继续轮询...")
            await page.wait_for_timeout(1000)

    await page.wait_for_timeout(200)
    return True


async def submit_assignment(page: Page) -> bool:
    """点击页面顶部的"提交作业"按钮，并处理确认弹窗。"""
    try:
        submit_btn = page.locator("header button").filter(has_text="提交作业")
        if await submit_btn.count() == 0:
            submit_btn = page.locator("header button").last
        await submit_btn.click(timeout=5000)
        await page.wait_for_timeout(1000)
    except Exception as e:
        logger.debug(f"  点击提交作业失败: {logger.summarize_exception(e)}")
        return False

    # 处理 Element Plus 确认弹窗
    try:
        dialog = page.locator(".el-dialog.confirm-service-dialog")
        await dialog.wait_for(state="visible", timeout=5000)
        confirm_btn = dialog.locator("footer .bg-\\[\\#0D0D0D\\]").first
        if await confirm_btn.count() == 0:
            confirm_btn = dialog.locator("footer div").last
        await confirm_btn.click(timeout=3000)
        await page.wait_for_timeout(2000)
        logger.info("  作业提交成功!")
        return True
    except PlTimeoutError:
        logger.info("  作业已提交（无确认弹窗）")
        return True
    except Exception as e:
        logger.debug(f"  处理提交弹窗失败: {logger.summarize_exception(e)}")
        return False
