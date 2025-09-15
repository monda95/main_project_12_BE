from pathlib import Path

from dotenv import load_dotenv

from .base import *  # noqa: F841

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env.prod")


DEBUG = False
