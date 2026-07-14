import os
from dotenv import load_dotenv

load_dotenv()

PROXY_DOMAIN = os.getenv("PROXY_DOMAIN", "potyjnovpn.apruxdomain.store")
HWID = os.getenv("HWID", "CB522960-E2A9-7A19-12CB-FD12FEC71E19")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ciorsa")

# Параметры по умолчанию
DEFAULT_CLIENT = "Happ"
DEFAULT_DEVICE = "Android"
