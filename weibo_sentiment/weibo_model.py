#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微博调用
"""

from __future__ import absolute_import, print_function

from snownlp import SnowNLP

from . import (
    settings,
    utils,
)

status_logger = utils.get_logger('status')
comment_logger = utils.get_logger('comments')


def get_all_statuses(weibo_client, uid):
    """获取授权用户 timeline 的所有 status
    """
    all_statuses = []
    done_status = set()
    status_count = 0
    current_page = 0
    max_id = None
    while True:
        status_logger.debug('all_status: uid: {uid}, max_id: {max_id}'.format(
                                uid=uid,
                                max_id=max_id))
        one_page_statuses = get_statuses_one_page(weibo_client, max_id)
        current_page += 1

        if not one_page_statuses.get('statuses'):
            break

        for status in one_page_statuses.get('statuses'):
            status_id = status['id']

            # weibo user_timeline api 分页使用max_id，next_cursor 貌似不能用
            # 但是 max_id 就会重复获取第一个
            if status_id in done_status:
                continue

            status_count += 1
            status_comments = get_comments(weibo_client, status_id, only_sentiment=True)
            all_statuses.append({
                'id': status['id'],
                'created_at': status['created_at'],
                'text': status['text'],
                'comments_sentiment': status_comments,
            })

            # 覆写 max_id 为最后一个 status
            max_id = status_id
        # 默认 count 为 5
        if len(one_page_statuses.get('statuses')) < 5:
            break

        if current_page >= settings.timeline_max_page:
            break
    return all_statuses

def get_statuses_one_page(weibo_client, max_id=None):
    """获取一页发布的微博
    """
    if max_id:
        statuses = weibo_client.statuses.user_timeline.get(max_id=max_id)
    else:
        statuses = weibo_client.statuses.user_timeline.get()
    return statuses

def get_comments(weibo_client, status_id, only_sentiment=True):
    """获取某一个微博的所有评论

    :param only_sentiment: 是否只返回平均后的情绪值
    """
    comments = []
    max_id = None
    current_page = 0
    comment_count = 0
    sentiment_value = 0
    while True:
        current_page += 1
        comments_json = get_comments_one_page(weibo_client=weibo_client,
                                                status_id=status_id,
                                                max_id=max_id)
        for comment in comments_json.get('comments', []):
            comment_count += 1
            if only_sentiment:
                sentiment_value += comment.get('sentiment', 0)
            else:
                comments.append({
                    'id': comment['id'],
                    'created_at': comment['created_at'],
                    'text': comment['text'],
                    'sentiment': comment.get('sentiment'),
                })
        # 下一页评论
        max_id = comments_json.get('next_cursor')
        if not max_id:
            break

        if current_page >= settings.comment_max_page:
            break

    # todo: 过滤掉自己的评论
    if only_sentiment:
        return sentiment_value if comment_count == 0 else sentiment_value/comment_count
    else:
        return comments

def get_comments_one_page(weibo_client, status_id, max_id=None, with_sentiment=True):
    """获取一页评论

    :param with_sentiment: 是否分析每条评论的情绪值
    """
    comment_logger.debug('status_id: {}, max_id: {}'.format(status_id, max_id))
    comments = None
    if max_id:
        comments = weibo_client.comments.show.get(id=status_id, max_id=max_id)
    else:
        comments = weibo_client.comments.show.get(id=status_id)

    if with_sentiment:
        for comment in comments.get('comments', []):
            text = comment['text']
            sentiment = analysis_sentiment(text)
            comment['sentiment'] = sentiment
    return comments

def analysis_sentiment(text):
    snow = SnowNLP(text)
    return snow.sentiments
