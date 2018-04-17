import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = os.environ.get('SSL_DISABLE') or True

    MAIL_SERVER =  os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT =  int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS =  bool(os.environ.get('MAIL_USE_TLS') or True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    CELERY_BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = 'amqp://'
    CELERY_TIMEZONE = 'America/Caracas'
    CELERY_ENABLE_UTC = True
    CELERY_RESULT_EXPIRES = 3600

    MONGO_HOST = os.environ.get('MONGO_HOST') or 'localhost'
    MONGO_PORT = int(os.environ.get('MONGO_PORT') or 27017)
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME') or 'wiki'
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD') or 'wiki123'
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME') or 'wiki_history_extractor'

    DEBUG = os.environ.get('DEBUG') or False
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    MONGO_DB_NAME = os.environ.get('MONGO_DB_TEST_NAME') or 'wiki_history_extractor_test'
    TESTING = True
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    MONGO_HOST = os.environ.get('MONGO_HOST') or 'mongo'

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'amqp://wiki:wiki123@rabbit:5672'

class DigitalOceanConfig(Config):
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_TIMEZONE = 'America/New_York'

class DockerConfig(Config):
    MONGO_HOST = os.environ.get('MONGO_HOST') or 'mongo'

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'amqp://wiki:wiki123@rabbit:5672'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'amqp://wiki:wiki123@rabbit:5672'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'digital_ocean': DigitalOceanConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}
