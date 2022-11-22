import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    INSTANCE_NAME = "europe-central2:devel-sql"
    PROJECT_ID = "devel-12345"
    PUBLIC_IP_ADDRESS = "127.0.0.1:3306"
    PASSWORD = "Bonvolu53"
    DBNAME = "Data"

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'svs-fem-secret-key'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
