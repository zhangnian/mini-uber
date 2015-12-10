# -*- coding: utf-8 -*-

import time
import hashlib

import uber



def check_user_exist(username):
	cursor = uber.g_db.cursor()
	try:
		cursor.execute("select count(1) from passengers where username='%s'" % username)
		nrow = int(cursor.fetchall()[0][0])
		return nrow > 0
	except Exception as e:
		return False
	finally:
		cursor.close()


def get_userid(username, password):
	cursor = uber.g_db.cursor()
	try:
		cursor.execute("select id from passengers where username = '%s' and password = '%s'" % (username, password))
		rows = cursor.fetchall()
		assert len(rows) == 1
		return rows[0][0]
	except Exception as e:
		return -1
	finally:
		cursor.close()


def update_token(userid):
	raw = '%d|%s|%s' % (int(time.time()), userid, uber.app.config['TOKEN_KEY'])
	m = hashlib.md5()
	m.update(raw)
	token = m.hexdigest()

	try:
		uber.g_redis.set('tokens::%s' % userid, token)
	except Exception as e:
		return None
	return token

