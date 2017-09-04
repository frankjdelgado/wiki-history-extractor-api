import os
basedir = os.path.abspath(os.path.dirname(__file__))

# template config with tweeks

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    CELERY_BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = 'amqp://'
    CELERY_TIMEZONE = 'AMERICA/CARACAS'
    CELERY_ENABLE_UTC = True
    CELERY_RESULT_EXPIRES = 3600

    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'wiki'
    MONGO_PASSWORD = 'wiki123'


    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    MONGO_HOST = 'mongo'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'wiki'
    MONGO_PASSWORD = 'wiki123'
    SSL_DISABLE = True

    CELERY_BROKER_URL = 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = 'amqp://wiki:wiki123@rabbit:5672'

class DigitalOceanConfig(Config):
    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_PORT = os.environ.get('MONGO_PORT')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    SSL_DISABLE = True

    CELERY_BROKER_URL = 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_TIMEZONE = 'America/New_York'

class DockerConfig(Config):
    MONGO_HOST = 'mongo'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'wiki'
    MONGO_PASSWORD = 'wiki123'
    SSL_DISABLE = True

    CELERY_BROKER_URL = 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = 'amqp://wiki:wiki123@rabbit:5672'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'digital_ocean': DigitalOceanConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}
