import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sivep_security_2026")

class TestConfig(Config):
    TESTING = True
