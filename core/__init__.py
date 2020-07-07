import time
from threading import Thread

from .async_pub import start_pub
from .oper_db import fetch_all_user

from config import END_HOUR
from config import START_HOUR
from config import DATETIME_FORMAT
from config import EVERY_WHILE_WAIT_TIME

# 整体间隔
_whole_interval = 60 * 60 * (END_HOUR - START_HOUR) // 100  # 5.4m


def main():
    圈 = 1

    while True:
        localtime = time.localtime()

        # 在此时间段之内不发布文章
        if localtime.tm_hour < START_HOUR or localtime.tm_wday in [0, 5, 6]:
            time.sleep(EVERY_WHILE_WAIT_TIME)
            print(f'等待中，北京时间: {time.strftime(DATETIME_FORMAT)}')
            continue

        # 所有可用的用户
        users = fetch_all_user()
        user_number = len(users)

        print(f'开始第{圈}圈，本轮获取{len(users)}个用户')

        # 每个用户之间的间隔
        every_user_interval = _whole_interval / user_number

        # 开始本轮发布
        for i, u in enumerate(users, 1):
            uid = u[0]

            # 开始异步发布
            task = Thread(target=start_pub, args=(u,), daemon=True)
            task.start()

            print(f'第{i}个用户已开始, uid: {uid}')

            # 等待本轮发布每篇文章的间隔时长
            time.sleep(every_user_interval)

        # 等待下一轮
        try:
            time.sleep(_whole_interval - every_user_interval * user_number)
        except ValueError:
            ...

        圈 += 1
