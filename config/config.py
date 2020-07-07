import os


def _gen_path(*args: str) -> 'An absolute path':
    # Generate an absolute path.
    return os.path.abspath(os.path.join(*args))


BASE_DIR = _gen_path(os.path.dirname(os.path.dirname(__file__)))

DB_DIR = _gen_path(BASE_DIR, 'db')
LOG_DIR = _gen_path(BASE_DIR, 'log')

# 文件编码
FE = 'UTF-8'

DATETIME_FORMAT = '%F %T'

BLOG_DOMAIN_NAME = 'blog.gqylpy.com'

# 每日发布文章的开始时间
START_HOUR = 9

# 每日发布文章的结束时间
END_HOUR = 23

# 在发布文章时间之外的每次循环等待时长
EVERY_WHILE_WAIT_TIME = 60 * 30
