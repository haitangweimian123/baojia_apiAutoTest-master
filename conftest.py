import os
import pytest
from py.xml import html
import time
# from playwright.sync_api import sync_playwright
from playwright.async_api import Page, Browser
import allure

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", time.strftime("%Y%m%d%H%M%S"))
print(OUTPUT_DIR)






# 骚操作，不建议这么写。用法是 fixtures("search_baidu")['kerwords']
# @pytest.fixture(scope="class")
# def fixtures():
#     """
#     测试数据，存放在fixtures目录下，这里是我习惯性引入 Cypress的概念，实际就是测试数据
#     :return:
#     """
#     def _fixtures(filename: str):
#         from common.tools import Tools
#         return Tools.get_fixtures(filename)
#
#     yield _fixtures

# ref: https://github.com/microsoft/playwright-pytest
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    pytest-playwrigt 内置钩子
    :param browser_context_args:
    :param tmpdir_factory:
    :return:
    """
    return {
        **browser_context_args,
        "record_video_dir": os.path.join(OUTPUT_DIR, "videos") #开始录制时并不知道测试结果正确与否，所以成功失败都会录制
        }

def pytest_addoption(parser):
    """
    接收命令行参数
    :param parser:
    :return:
    """
    parser.addoption("--env", action="store", dest="environment", default="dev", help="environment: dev, dev-01, prod")


def pytest_configure(config):
    """
    初始化配置，最先执行
    :param config:
    :return:
    """

    # 添加接口地址与项目名称
    config._metadata["项目名称"] = "报价系统"
    config._metadata["项目地址"] = "http://10.0.88.13/proQuotedManagement/index"


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
    用于向测试用例中添加用例的开始时间、内部注释，和失败截图等.
    :param item:
    """

    pytest_html = item.config.pluginmanager.getplugin('html')
    callers = yield
    report = callers.get_result()
    report.description = description_html(item.function.__doc__)
    report.extra = []

    if "page" not in item.funcargs:
        return "page not in item.funcargs"
    page = item.funcargs["page"]
    if report.when == 'call':
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            case_name = report.nodeid.replace("::", "_") + ".png"
            image_relative_path = os.path.join("images", case_name.replace('testcase/', ''))
            image_absolute_path = os.path.join(OUTPUT_DIR, image_relative_path)
            capture_screenshots(image_absolute_path, page)
            if image_relative_path:
                html = '<div><img src="%s" alt="screenshot" style="height:360px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % image_relative_path
                report.extra.append(pytest_html.extras.html(html))

# TODO: 使用 allure 以更好的呈现截图与视频
# ref: https://zenn.dev/yusukeiwaki/articles/cfda648dc170e5
# @pytest.mark.hookwrapper
# def pytest_runtest_makereport(item, call):
#     """
#     用于向测试用例中添加用例的开始时间、内部注释，和失败截图等.
#     :param item:
#     """
#     if call.when == "call":
#         # 失败的情况下
#         if call.excinfo is not None and "page" in item.funcargs:
#             from playwright.async_api import Page
#             page: Page = item.funcargs["page"]
#
#             allure.attach(
#                 page.screenshot(type='png'),
#                 name=f"{slugify(item.nodeid)}.png",
#                 attachment_type=allure.attachment_type.PNG
#             )
#
#             video_path = page.video.path()
#             page.context.close()  # ensure video saved
#             allure.attach(
#                 open(video_path, 'rb').read(),
#                 name=f"{slugify(item.nodeid)}.webm",
#                 attachment_type=allure.attachment_type.WEBM
#             )
#
#     callers = yield

@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """
    设置用例描述表头
    :param cells:
    :return:
    """
    cells.insert(2, html.th('Description'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """
    设置用例描述表格
    :param report:
    :param cells:
    :return:
    """

    cells.insert(2, html.td(report.description if hasattr(report, "description") else ""))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_report_title(report):
    """
    pytest-html，自定义报告标题
    :param report:
    :return:
    """

    # 报告名称
    report.title = "报价系统V1.1.5.0 测试报告"

    # 重写报告地址
    # 开启这个之后，无论--html传入什么地址都只会在根目录生成报告
    report.logfile = f'{OUTPUT_DIR}/{time.strftime("%Y%m%d")}_report.html'


@pytest.mark.optionalhook
def pytest_html_results_summary(prefix):
    """
    pytest-html，自定义 Summary 部分。也可以用于注入一些报告样式。
    :return:
    """
    prefix.extend([html.p("所属部门: 质量部")])
    prefix.extend([html.p("测试人员: xxxx")])
    prefix.extend(
        [
            html.style(
                """
    /* 自定义样式 */

    body, #results-table {
        font-size: 15px;
    }

    /*  */
    """
            )
        ]
    )


def description_html(desc):
    """
    将用例中的描述转成HTML对象
    :param desc: 描述
    :return:
    """
    if desc is None:
        return "No case description"
    desc_ = ""
    for i in range(len(desc)):
        if i == 0:
            pass
        elif desc[i] == '\n':
            desc_ = desc_ + ";"
        else:
            desc_ = desc_ + desc[i]

    desc_lines = desc_.split(";")
    desc_html = html.html(
        html.head(
            html.meta(name="Content-Type", value="text/html; charset=latin1")),
        html.body(
            [html.p(line) for line in desc_lines]))
    return desc_html


def capture_screenshots(image_path, page):
    """
    配置用例失败截图路径
    :param case_name: 用例名
    :return:
    """

    image_dir = os.path.dirname(image_path)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    try:
        page.screenshot(path=image_path)
    except Exception as e:
        print(f'截图失败 {e}')


if __name__ == "__main__":
    pass
