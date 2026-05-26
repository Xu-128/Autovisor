# encoding=utf-8
"""
Autovisor Auto-Handle — 智慧树全自动做题模块。

流程: 登录 → 导航到课程作业页 → 找到未完成作业 → 点击"去完成" →
      确认页点击"继续答题" → 做题页通过 DeepSeek API 答题 → 提交。
"""
import asyncio

from playwright.async_api import async_playwright, Page
from playwright._impl._errors import TargetClosedError

from modules.configs import Config
from modules.logger import Logger
from modules.utils import (
    get_runtime_path, save_cookies, load_cookies, clear_cookies,
    hide_window,
)
from modules.slider import slider_verify
from modules.tasks import wait_for_verify
from modules.handler import (
    answer_all_questions, submit_assignment,
)
from modules.deepseek_client import DeepSeekClient
from modules import installer

logger = Logger()
config = Config("configs.ini")
COOKIE_PATH = get_runtime_path("res", "cookies.json")


def print_banner():
    print("""
    ╔══════════════════════════════════════╗
    ║        Autovisor - Auto Handle       ║
    ║       智慧树全自动做题模块           ║
    ╚══════════════════════════════════════╝
    """, flush=True)


async def init_page(p, cookies=None):
    """初始化浏览器、上下文和页面。参考 Autovisor.py 的同名函数。"""
    driver = "msedge" if config.driver == "edge" else config.driver
    launch_args = {
        "channel": driver,
        "headless": False,
        "executable_path": config.exe_path if config.exe_path else None,
        "args": [
            '--window-size=1600,900',
            '--window-position=100,100',
        ],
    }
    browser = await p.chromium.launch(**launch_args)

    try:
        context = await browser.new_context()
    except TargetClosedError:
        await asyncio.sleep(1)
        browser = await p.chromium.launch(**launch_args)
        context = await browser.new_context()

    if cookies:
        await context.add_cookies(cookies)

    page = await context.new_page()

    with open('res/stealth.min.js', 'r', encoding='utf-8') as f:
        js = f.read()
    await page.add_init_script(js)
    page.set_default_timeout(24 * 3600 * 1000)

    return page, context, browser


async def auto_login(context, page, modules=None):
    """自动登录。参考 Autovisor.py 的同名函数。"""
    cookie_saved = False

    async def request_handler(request):
        nonlocal cookie_saved
        if cookie_saved:
            return
        if "https://www.zhihuishu.com" in request.url:
            cookies = await context.cookies()
            save_cookies(cookies, COOKIE_PATH)
            cookie_saved = True

    page.on('request', request_handler)
    await page.goto(config.login_url, wait_until="commit")

    if "login" not in page.url:
        return True

    await page.wait_for_selector(".wall-main", state="attached", timeout=15000)

    if config.username and config.password:
        await page.fill("#lUsername", config.username)
        await page.fill("#lPassword", config.password)
        await page.click(".wall-sub-btn")

    if config.enableAutoCaptcha and modules:
        await slider_verify(page, modules)

    try:
        await page.wait_for_selector(".wall-main", state="hidden", timeout=60000)
    except Exception:
        pass

    return False


async def ensure_login(context, page, cookies, modules=None):
    """确保已登录，cookie 失效则重新登录。"""
    if cookies:
        await page.goto(config.login_url, wait_until="commit")
        await page.wait_for_timeout(1500)
        if "login" not in page.url:
            logger.info("使用 Cookies 登录成功!")
            return True
        logger.warn("检测到 Cookies 已失效, 将重新登录.", shift=True)
        clear_cookies(COOKIE_PATH)
        cookies = None

    if not config.username or not config.password:
        logger.info("请手动填写账号密码...")
    logger.info("正在等待登录完成...")
    await auto_login(context, page, modules)
    logger.info("登录成功!")
    return False


async def handle_task_list(page, context, deepseek_client, auto_submit=False):
    """处理作业列表页：找到所有未完成作业，逐个点击、做题、提交。"""
    await page.wait_for_selector(".task-type-list", state="attached", timeout=30000)
    await page.wait_for_timeout(2000)

    # 确保在"作业"tab 且筛选"未完成"
    try:
        task_tabs = page.locator(".task-type-item")
        if await task_tabs.count() >= 1:
            homework_tab = task_tabs.first
            is_active = await homework_tab.get_attribute("class")
            if "active" not in (is_active or ""):
                await homework_tab.click()
                await page.wait_for_timeout(1000)
    except Exception:
        pass

    try:
        status_filter = page.locator(".status .name").first
        is_active = await status_filter.get_attribute("class")
        if "active" not in (is_active or ""):
            await status_filter.click()
            await page.wait_for_timeout(1000)
    except Exception:
        pass

    go_buttons = page.locator(".status-btn.primary").filter(has_text="去完成")
    total = await go_buttons.count()
    logger.info(f"检测到 {total} 个未完成作业")

    if total == 0:
        logger.info("所有作业已完成!")
        return

    for i in range(total):
        go_buttons = page.locator(".status-btn.primary").filter(has_text="去完成")
        if await go_buttons.count() == 0:
            break

        btn = go_buttons.first
        try:
            title_el = btn.locator("..").locator("..").locator(".info .title").first
            title = await title_el.text_content()
            title = title.strip() if title else f"作业{i+1}"
        except Exception:
            title = f"作业{i+1}"

        logger.info(f"\n{'='*60}")
        logger.info(f"正在处理: {title} ({i+1}/{total})")
        logger.info(f"{'='*60}")

        list_url = page.url

        # 监听新标签页
        new_page = None

        async def handle_popup(popup):
            nonlocal new_page
            new_page = popup

        context.on("page", handle_popup)

        try:
            await btn.click(timeout=5000)
            await page.wait_for_timeout(2000)

            if new_page and new_page != page:
                logger.info("检测到新标签页，切换到新页面...")
                page = new_page
        except Exception as e:
            logger.log_exception(f"点击'去完成'失败: {title}", e)
            continue
        finally:
            context.remove_listener("page", handle_popup)

        # --- 中间页 / 确认页 → 点击继续/开始按钮 ---
        await _click_continue_button(page)

        # --- 做题页面 ---
        on_exam_page = await _wait_for_exam_page(page)
        if not on_exam_page:
            logger.warn("未能进入做题页面，跳过此作业")
            try:
                await page.goto(list_url, wait_until="commit")
                await page.wait_for_timeout(2000)
            except Exception:
                pass
            continue

        # 回答所有题目
        try:
            answered = await answer_all_questions(page, deepseek_client)
        except Exception as e:
            logger.log_exception("答题过程出错", e)
            answered = 0

        # 提交前确认
        if auto_submit:
            logger.info(f"共作答 {answered} 题，自动提交作业...")
            try:
                await submit_assignment(page)
            except Exception as e:
                logger.log_exception("提交作业出错", e)
        else:
            confirm = input(f"\n  共作答 {answered} 题，是否提交作业？[Y/n]: ").strip().lower()
            if confirm == '' or confirm == 'y' or confirm == 'yes':
                try:
                    await submit_assignment(page)
                except Exception as e:
                    logger.log_exception("提交作业出错", e)
            else:
                logger.info("已取消提交，返回列表页")

        # 回到列表页
        try:
            await page.goto(list_url, wait_until="commit")
            await page.wait_for_timeout(2000)
        except Exception:
            pass


async def _click_continue_button(page: Page):
    """在确认/中间页点击继续答题或开始答题按钮。"""
    await page.wait_for_timeout(1500)
    current_url = page.url
    logger.debug(f"  当前页面 URL: {current_url[:100]}")

    # 如果已经在做题页面，不需要任何操作
    if "examloop" in current_url or "examLoop" in current_url:
        return

    # 如果在 testDetail 页面，找继续/开始按钮
    if "testDetail" in current_url or "singleCourse" in current_url:
        # 按文本查找按钮（"继续答题" 或 "开始答题"）
        for btn_text in ["继续答题", "开始答题", "继续"]:
            try:
                btn = page.locator(f"text={btn_text}").first
                if await btn.count() > 0:
                    await btn.click(timeout=5000)
                    logger.info(f"点击'{btn_text}'按钮...")
                    await page.wait_for_timeout(2000)
                    return
            except Exception:
                continue

    logger.debug("  未找到继续/开始按钮，尝试直接进入做题页...")


async def _wait_for_exam_page(page: Page) -> bool:
    """等待进入做题页面。返回是否成功。"""
    for attempt in range(5):
        current_url = page.url
        if "examloop" in current_url or "examLoop" in current_url:
            logger.info("进入做题页面...")
            await page.wait_for_timeout(2000)
            return True
        await page.wait_for_timeout(2000)

    logger.debug(f"  最终 URL: {page.url[:120]}")
    return False


async def main():
    """主异步入口。"""
    print_banner()

    # 验证配置
    urls = config.get_auto_handle_urls()
    if not urls:
        logger.error("未配置有效的课程链接，请在 configs.ini [auto-handle-url] 中设置")
        return

    if not config.deepseek_api_key:
        logger.error("未配置 DeepSeek API Key，请在 configs.ini [deepseek] 中设置 api_key")
        return

    deepseek_client = DeepSeekClient(
        api_key=config.deepseek_api_key,
        model=config.deepseek_model,
    )
    logger.info(f"DeepSeek 客户端初始化成功 (model: {config.deepseek_model})")

    # 启动时选择提交模式
    print()
    choice = input("是否在每题作答后自动提交？[y/N]: ").strip().lower()
    auto_submit = choice in ('y', 'yes')
    if auto_submit:
        logger.info("提交模式: 自动提交")
    else:
        logger.info("提交模式: 手动确认")

    cookies = load_cookies(COOKIE_PATH)
    modules = installer.start()

    async with async_playwright() as p:
        page, context, browser = await init_page(p, cookies)

        if config.enableHideWindow:
            await hide_window(page)

        try:
            await ensure_login(context, page, cookies, modules)

            # 启动 CAPTCHA 监控后台任务
            event_loop_verify = asyncio.Event()
            verify_task = asyncio.create_task(
                wait_for_verify(page, config, event_loop_verify)
            )

            for url in urls:
                logger.info(f"正在加载课程: {url}")
                await page.goto(url, wait_until="commit")
                await page.wait_for_timeout(2000)

                # 检查是否被重定向到登录页
                if "login" in page.url or "passport" in page.url:
                    logger.warn("会话过期，重新登录...")
                    clear_cookies(COOKIE_PATH)
                    await ensure_login(context, page, None, modules)
                    await page.goto(url, wait_until="commit")
                    await page.wait_for_timeout(2000)

                await handle_task_list(page, context, deepseek_client, auto_submit)

            # 清理
            verify_task.cancel()
            try:
                await verify_task
            except asyncio.CancelledError:
                pass

        except TargetClosedError:
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.log_exception("程序运行出错", e)
        finally:
            # 保存 cookies
            try:
                cookies = await context.cookies()
                save_cookies(cookies, COOKIE_PATH)
            except Exception:
                pass
            await browser.close()

    logger.info("Auto Handle 执行完毕.")


if __name__ == "__main__":
    asyncio.run(main())
