from celery import Celery
from src.config import Config

# celery = Celery(
#     broker=Config.REDIS_URL,
#     backend=Config.REDIS_URL,

# )

# c_app.config_from_object('src.config): to set celery configuration from a config.py
# celery.conf.update(
#     task_serializer='json'
# )
