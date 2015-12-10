# -*- coding: utf-8 -*-


class Config(object):
    DEBUG = False
    TESTING = False
    DB_FILE = '/tmp/uber.db'
    REDIS_IP = '58.67.219.143'
    REDIS_PORT = 6379
    TOKEN_KEY = 'thisistokenkeyusedforgeneratetoken'


class DevelopmentConfig(Config):
    DEBUG = True
    REDIS_IP = '58.67.219.143'
    REDIS_PORT = 6379
    USER_PWD = '123456'