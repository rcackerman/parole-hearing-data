
class Config(object):
    CSRF_ENABELED = True
    DATABASE_URL = 'postgresql://jane@localhost:5432/parole'
    DEBUG = False
    DEVELOPMENT = True
    TESTING = False


class ProductionConfig(Config):
    DATABASE_URL = ''
    DEBUG = False


class StagingConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):
    Testing = True
