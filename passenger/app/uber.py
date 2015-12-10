# -*- coding: utf-8 -*-

from flask import Flask, request, g, make_response, abort
from comm import make_succ, make_err
import sys
import redis
import datetime
import config
import MySQLdb


from error_def import *
from user import *


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

g_redis = redis.Redis(host='58.67.219.143', port=6379)
g_db = MySQLdb.connect('10.66.160.96', 'root', 'vvshop!@#', 'test', charset='utf8')


import logging
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('./uber.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)



@app.before_request
def before_request_handler():
    """解密、认证、过载保护、防刷
    """
    g.ts = datetime.datetime.now().microsecond

    if '/register' in request.url or '/login' in request.url:
        return

    g.userid = request.args.get('userid')
    token = request.args.get('token')
    if not g.userid or not token:
        return make_err(10001, "未传入userid或token")

    try:
        ret = g_redis.get('tokens::%s' % g.userid)
    except Exception as e:
        return make_err(20001, "redis error")

    if ret != token:
        return make_err(20002, "token验证失败")

    return


@app.after_request
def after_request_handler(response):
    """ 统计、加密、日志
    """
    cost = (datetime.datetime.now().microsecond - g.ts) / 1000
    print 'cost: %dms' % cost
    return response


@app.route('/call_taxi', methods=['GET'])
def call_taxi():
    """ 用户叫车
    """
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    dest = request.args.get("dest")

    if not longitude or not latitude or not dest:
        return make_err(-1, "参数不合法")
    
    cursor = g_db.cursor()
    try:
        sql = 'insert into orders(userid, dest_address, longitude, latitude, status, create_ts)' \
              'values(%s, "%s", %f, %f, 0, unix_timestamp(now()))'
        cursor.execute(sql % (g.userid, dest, float(longitude), float(latitude)))
        g_db.commit()
    except Exception as e:
        app.logger.error("exception: %s" % str(e))
        return make_err(-1, "mysql error")
    finally:
        cursor.close()

    app.logger.debug('this is the log')
    return make_succ()


@app.route('/register', methods=['GET'])
def register():
    username = request.args.get('username')
    password = request.args.get('password')
    if not username or not password:
        return make_err(ERR_REQUEST_ARGS, "用户名或密码为空")

    if check_user_exist(username):
        return make_err(10003, "用户已注册")

    try:   
        cursor = g_db.cursor()    
        cursor.execute("insert into passengers(username, password, status) values('%s', '%s', 0)" % (username, password))
        g_db.commit()
    except Exception as e:
        app.logger.error("exception: %s" % str(e));
        return make_err(10002, "用户注册失败")
    finally:
        cursor.close()

    return make_succ()


@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    if not username or not password:
        return make_err(ERR_REQUEST_ARGS, "用户名或密码为空")

    userid = get_userid(username, password)
    if userid == -1:
        return make_err(10004, "用户名或密码错误")

    token = update_token(userid)
    if not token:
        return make_err(-1, "更新token失败")

    data = {"userid":userid, "token":token}
    return make_succ(data)