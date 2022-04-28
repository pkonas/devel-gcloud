from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
import rq
from redis import Redis

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('dtwin-tasks', connection=app.redis)

from dtwin_web import routes,models

