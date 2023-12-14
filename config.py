import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = "mysql://admin:It12345!@team3-db-01.cluster-c1eiqtt31v98.ap-northeast-2.rds.amazonaws.com/recapark"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"
