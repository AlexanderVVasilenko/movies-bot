import os

import redis
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


class SiteSettings(BaseSettings):
    api_key: SecretStr = os.getenv("SITE_API", None)

