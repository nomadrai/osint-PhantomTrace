from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    hibp_api_key: Optional[str]
    hibp_user_agent: str


def get_settings() -> Settings:
    api_key = os.getenv("HIBP_API_KEY")
    user_agent = os.getenv("HIBP_USER_AGENT", "PhantomTrace/1.0 (contact: you@example.com)")
    return Settings(hibp_api_key=api_key, hibp_user_agent=user_agent)
