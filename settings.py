import os

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class SiteSettings(BaseSettings):
    api_key: SecretStr = os.getenv("SITE_API", None)
