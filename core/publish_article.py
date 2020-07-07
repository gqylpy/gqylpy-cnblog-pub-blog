import re
import uuid
import requests
from threading import Lock
from tools import gen_path

from config import FE
from config import LOG_DIR

lock = Lock()
_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'


class PublishArticle:
    err = [
        '博客园用户登录',
        '相同标题的内容已存在！',
        '禁止评论的随笔不允许发到首页候选区',
        '少于150字的随笔不允许发布到首页候选区',
        '抱歉！已超过当日博文发布数量100篇限制！今天无法继续发布！',
        '抱歉！已超过当日博文发布数量限制！',  # 早晨出现这个错误
        '抱歉！已达当日博文发布数限制！',  # 报错时间: 19:40 - 23:45
        # 'Post operation failed. The error message related to this problem was as follows: Input string was not in a correct format.',
    ]

    def __init__(self, cookie: str, title: str, content: str):
        if len(content) < 150:
            content += '_' * 150

        self.headers = {
            'User-Agent': _user_agent + str(uuid.uuid4()),
            'Cookie': cookie,
        }

        self.data = {
            '__VIEWSTATE': '',
            '__VIEWSTATEGENERATOR': 'FE27D343',
            'Editor$Edit$txbTitle': title,
            'Editor$Edit$EditorBody': content,
            'Editor$Edit$Advanced$ckbPublished': 'on',
            'Editor$Edit$Advanced$chkDisplayHomePage': 'on',
            'Editor$Edit$Advanced$chkMainSyndication': 'on',
            'Editor$Edit$Advanced$txbEntryName': '',
            'Editor$Edit$Advanced$txbExcerpt': '',
            'Editor$Edit$Advanced$tbEnryPassword': '',
            'Editor$Edit$lkbPost': '发布',
            'Editor$Edit$Advanced$chkComments': 'no',  # 允许评论
            'Editor$Edit$APOptions$APSiteHome$cbHomeCandidate': '',  # 发布至首页候选区
            'Editor$Edit$Advanced$txbTag': '我的转发',  # 标签
        }

        self.title = title
        self.ar_id = None
        self.err_info = None

    def startup(self) -> bool:
        # Start publish article
        response = requests.post(
            'https://i.cnblogs.com/EditPosts.aspx?opt=1',
            headers=self.headers,
            data=self.data
        )
        return self.check(response.text)

    def check(self, page_text: str):
        # Check whether the publication has passed.
        try:
            # Save the article link
            self.ar_id = re.search('3D(?P<aid>\d{8})?">', page_text).group('aid')
        except AttributeError:
            for err_info in self.err:
                if err_info in page_text:
                    self.err_info = err_info
                    break
            else:
                self.err_info = '未知错误'
                self.record_unerr(page_text)
            return False
        return True

    def record_unerr(self, page_text: str):
        # Record unknown error
        fp = open(gen_path(LOG_DIR, f'{self.title}.html'), 'w', encoding=FE)
        fp.write(page_text)
        fp.close()
