# written by brian
# used with the test_config parameter of create_app

# base
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	# Randomized secret key
	SECRET_KEY = os.urandom(24)
	
	# sqlalchemy stuff
	SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
	RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
	
class TestingConfig(Config):
	# static secret key for testing
	SECRET_KEY = "secret-key"
	
	# in-memory database for testing
	SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
	WTF_CSRF_ENABLED = False
