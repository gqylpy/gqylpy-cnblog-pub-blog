from tools import db
from tools import exec_sql

_gqy_uid = 6

# 被停用但仍可访问的用户
_not_uid = (1, 2)


def fetch_all_user() -> tuple:
    # Fetch all user.
    return exec_sql(f'''
        SELECT id, total_disposed, now_bid, cookie, home 
        FROM user_cnblog 
        WHERE is_ok IS TRUE 
          AND home IS NOT NULL
          AND DATE_ADD(create_date, INTERVAL 1 DAY) < NOW()  -- 过滤注册时间小于1天的用户
        HAVING id NOT IN {str(_not_uid)}
          AND now_bid < {fetch_max_bid()[0]} -- 过滤已发布所有文章的用户
        ORDER BY id DESC;
    ''', database=db.gqylpy)


def fetch_a_blog(bid: int) -> tuple:
    # Random fetch a blog.
    return exec_sql(f'''
        SELECT blog.id, blog.title, article.markdown_content
        FROM blog INNER JOIN article
        ON blog.content_id = article.id 
        WHERE blog.user_id = {_gqy_uid}
          AND blog.is_private = FALSE 
          AND blog.is_draft = FALSE 
          AND blog.is_delete = FALSE 
          AND blog.access_password is NULL 
        HAVING blog.id > {bid}
        ORDER BY id
        LIMIT 0, 1;
    ''', fetchone=True, database=db.hello_world)


def fetch_a_rsc(rid: int) -> tuple:
    # Random fetch a resource.
    return exec_sql(f'''
        SELECT id, name, cnblog 
        FROM resources 
        WHERE id != 1
        HAVING id > {rid}
        ORDER BY id
        LIMIT 0, 1;
    ''', fetchone=True, database=db.gqylpy)


def fetch_max_bid() -> tuple:
    # Fetch the max blog id.
    return exec_sql(f'''
        SELECT MAX(id)
        FROM blog
        WHERE user_id = {_gqy_uid}
          AND blog.is_private = FALSE 
          AND blog.is_draft = FALSE 
          AND blog.is_delete = FALSE 
          AND blog.access_password is NULL;
    ''', fetchone=True, database=db.hello_world)


def fetch_max_rid() -> tuple:
    # Fetch the max resource id.
    return exec_sql(f'''
        SELECT MAX(id) 
        FROM resources;
    ''', fetchone=True, database=db.gqylpy)


def record_ar_link(link: str, uid: int) -> int:
    # Record the article link.
    return exec_sql(f"""
        INSERT INTO archive_cnblog(link, uid) 
        VALUES {str((link, uid))};
    """, commit=True, database=db.gqylpy)


def update_now_bid(uid: int, bid: int) -> int:
    # Update now blog id.
    return exec_sql(f'''
        UPDATE user_cnblog
        SET now_bid = {bid},
         total_disposed = total_disposed + 1 -- 总量+1
        WHERE id = {uid};
    ''', commit=True, database=db.gqylpy)


def fetch_gqy_blog_path() -> tuple:
    # Fetch the gqy user id.
    return exec_sql(f'''
        SELECT blog_path
        FROM user
        WHERE id = {_gqy_uid};
    ''', fetchone=True, database=db.hello_world)
