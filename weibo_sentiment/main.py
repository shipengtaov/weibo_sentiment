#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微博情绪分析
"""

from __future__ import absolute_import, print_function

import sys
from os.path import dirname, abspath
from os import path
import json
import datetime
import time
from functools import wraps

from flask import (
    Flask, request, session, g, redirect, url_for, render_template,
)

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from weibo_sentiment.packages.sinaweibopy.weibo import APIClient
from weibo_sentiment import (
    settings,
    utils,
    weibo_model,
)

app = Flask(__name__, static_url_path='/static')
app.config.from_object(settings)

weibo_client = APIClient(app_key=settings.app_key,
                        app_secret=settings.app_secret,
                        redirect_uri=settings.redirect_url)

logger = utils.get_logger(__name__)


@app.before_request
def before_request():
    if hasattr(settings, 'google_analytics_script'):
        g.google_analytics_script = settings.google_analytics_script

    g.weibo_url = settings.follow_weibo

    if session.get('uid') \
                and session.get('access_token') \
                and session.get('expires_in') \
                and session.get('name'):
        g.uid = session['uid']
        g.access_token = session['access_token']
        g.expires_in = session['expires_in']
        g.name = session['name']
        g.screen_name = session['screen_name']
        weibo_client.set_access_token(g.access_token, g.expires_in)
    else:
        g.uid = None
        g.access_token = None
        g.expires_in = None
        g.name = None
        g.screen_name = None

@app.teardown_request
def after_request(response):
    return response

#-------------------------------- decorators ---------------------------------#

def authorize_required(fn):
    """decorator: 必须微博授权
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        if not g.access_token:
            return redirect(url_for('home'))
        res = fn(*args, **kwargs)
        return res
    return decorator

def make_sure_expires(fn):
    """decorator: 授权过期后跳转到授权页
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        now = datetime.datetime.now()
        if hasattr(g, 'expires_in'):
            expires_in = datetime.datetime.fromtimestamp(g.expires_in)
            if expires_in <= now:
                return redirect(url_for('weibo_signin'))
        return fn(*args, **kwargs)
    return decorator

#------------------------------ decorators end -------------------------------#

@app.route('/weibo/signin/', endpoint='weibo_signin', methods=['GET'])
def weibo_signin():
    """跳转到微博授权页
    """
    return redirect(weibo_client.get_authorize_url())

@app.route('/callback/', endpoint='weibo_callback', methods=['GET'])
def callback():
    """微博授权回调页
    """
    code = request.args.get('code', '')

    if not code:
        return 'missing code param. dada.dada..da...da......'

    r = weibo_client.request_access_token(code)
    logger.debug('access token: %s' % json.dumps(r))

    access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
    weibo_client.set_access_token(access_token, expires_in)

    user_info = weibo_client.users.show.get(uid=uid)

    logger.debug('got user: %s' % uid)

    save_access_token(uid=uid, access_token=access_token, expires_in=expires_in,
                        name=user_info['name'],
                        screen_name=user_info['screen_name'])
    # 授权以后直接进入情绪分析页
    return redirect(url_for('analysis'))
    # return redirect(url_for('home'))

def save_access_token(uid, access_token, expires_in, name, screen_name):
    """保存 access_token 信息
    """
    session['uid'] = uid
    session['access_token'] = access_token
    session['expires_in'] = expires_in
    session['name'] = name
    session['screen_name'] = screen_name
    return True

@app.route('/callback/cancel/', endpoint='weibo_callback_cancel', methods=['GET'])
def callback_cancel():
    """微博取消授权回调页
    """
    session['uid'] = None
    session['access_token'] = None
    session['expires_in'] = None
    return "已取消授权"

@app.route('/', endpoint='home', methods=['GET'])
def home():
    weibo_signin_url = url_for('weibo_signin')
    return render_template('index.html', **locals())

@app.route('/analysis/', endpoint='analysis', methods=['GET'])
@make_sure_expires
@authorize_required
def analysis():
    if not g.access_token:
        return redirect(url_for('home'))

    title = u'{} 粉丝的分析结果'.format(g.name)
    user_timeline_has_status = False

    start_time = time.time()

    all_statuses = weibo_model.get_all_statuses(weibo_client=weibo_client, uid=g.uid)

    # 消耗时间
    end_time = time.time()
    time_cost = end_time - start_time

    dates = []
    sentiments = []
    for i in all_statuses:
        dates.append(utils.format_weibo_time(i['created_at']))
        sentiments.append(round(i['comments_sentiment'], 2))

    dates_str = ','.join(dates)
    sentiments_str = ','.join(map(str, sentiments))

    if sentiments:
        user_timeline_has_status = True

    return render_template('analysis.html', **locals())

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 5000
    app.run(port=port)
