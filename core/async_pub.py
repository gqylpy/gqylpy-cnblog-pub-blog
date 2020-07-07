import re
import random
from urllib.parse import unquote

from .oper_db import fetch_a_blog
from .oper_db import record_ar_link
from .oper_db import update_now_bid
from .oper_db import fetch_gqy_blog_path
from .publish_article import PublishArticle

from tools import gen_path

from config import FE
from config import LOG_DIR
from config import BLOG_DOMAIN_NAME


def start_pub(user: tuple):
    try:
        return main_logic(user)
    except Exception as e:
        aborted_log('程序异常', e)


def main_logic(user: tuple):
    uid, total_disposed, now_bid, cookie, home = user

    # 用户主页地址
    blog_path = re.search(r'https://www\.cnblogs\.com/(?P<bp>.+?)/', home).group('bp')

    # 如果该用户已发布过所有文章，则从头再来
    # now_bid = now_bid if now_bid < fetch_max_bid()[0] else 0

    # 获取并更新文章
    bid, title, content = _replace_blog(*fetch_a_blog(now_bid))

    # 开始发布
    pa = PublishArticle(cookie, title, content)
    rst = pa.startup()

    if rst:
        update_now_bid(uid, bid)
        record_ar_link(f'https://www.cnblogs.com/{blog_path}/p/{pa.ar_id}.html', uid)

    else:
        aborted_log(title, pa.err_info, uid)


def _replace_blog(bid: int, title: str, content: str) -> tuple:
    # Update title and content
    title = unquote(title)
    content = unquote(content)
    blog_path = fetch_gqy_blog_path()[0]

    # 生成原文链接
    origin_link = f'''
        <h2>原文: 
            <a href="http://{BLOG_DOMAIN_NAME}/{blog_path}/{bid}" style="color: blue;">
                http://{BLOG_DOMAIN_NAME}/{blog_path}/{bid}
            </a>
        </h2>
    '''.strip()

    # 更新文章标题，防止重名
    title += f' {gen_ran_str()}'

    # 删除WLMJ
    content = re.sub(
        r'^.+<font color=black>传说中的武林秘籍：__<kbd>.+?</kbd>__</font>(\n)?(\n)?',
        '', content, 1, re.S
    )

    # 更新图片链接
    content = content.replace('/media/ai/', f'http://{BLOG_DOMAIN_NAME}/media/ai/')

    # 将链接添加至content
    content = f'{origin_link}\n\n{content}\n\n{origin_link}'

    return bid, title, content


def gen_ran_str() -> str:
    # Generate an random string.
    return chr(random.randint(65535, 655350))


def aborted_log(title: str, err_info, uid: int = 0):
    # 记录失败原因
    fp = open(gen_path(LOG_DIR, 'aborted.log'), 'a', encoding=FE)
    fp.write(f'{uid} {title}, {err_info}\n')
    fp.close()
