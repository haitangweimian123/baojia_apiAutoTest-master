
import os
import shutil
from loguru import logger

from test_main import rfc
from test_main import pytest
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def run(email: bool = True, web: bool = False):
    """
    启动测试
    :param email: 是否发送邮件
    :param web: 是否已服务形式打开报告（将忽略邮件服务）
    :return:
    """
    if os.path.exists("report/"):
        shutil.rmtree(path="report/")

    # 解决 issues 句柄无效
    logger.remove()
    file_path = rfc.get_config("$.file_path").current
    logger.add(file_path["log"], enqueue=True, encoding="utf-8")
    logger.info(
        """
                 _    _         _      _____         _
  __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
 / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
| (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
 \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
      |_|
      Starting      ...     ...     ...
    """
    )
    # pytest.main(["-v", "-s",'--html=report.html'])

    pytest.main(args=[f'--alluredir={file_path["report"]}/data'])


    if web:
        # 自动以服务形式打开报告
        os.system(f'allure serve {file_path["report"]}/data')
        # os.system(f'allure open {file_path["report"]}/data')
    else:
        # 本地生成报告
        os.system(
            f'allure generate {file_path["report"]}/data -o {file_path["report"]}/html --clean'
        )
        logger.success("报告已生成")

        if email:
            from core import EmailServe

            EmailServe(rfc).serve()


if __name__ == "__main__":
    run()
