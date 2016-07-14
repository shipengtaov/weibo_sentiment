# -*- coding: utf-8 -*-

from urlparse import urljoin

# sina
app_key = 'your app key'
app_secret = 'your app secret'

base_url = 'http://your_domain.org'

# 微博回调地址，这里为 /callback
redirect_url = urljoin(base_url, '/callback/')

# 推荐关注的微博账号 url
follow_weibo = 'http://weibo.com/5392656781'

# 每页5条
timeline_max_page = 10
# 每页50条
comment_max_page = 4

google_analytics_script = ""


DEBUG = True
SECRET_KEY = 'sina comment sentiment analysis'
