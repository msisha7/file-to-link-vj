import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get("API_ID", "25728264"))
API_HASH = environ.get("API_HASH", "7716997c3f0ef421c6bc23cd95c640d8")
BOT_TOKEN = environ.get("BOT_TOKEN", "7666348795:AAEt4PGr5e-vJsb6x0yrt_O4KlQf0EaF0pI")
FSUB = bool(environ.get('FSUB', True))

# Bot settings
PORT = environ.get("PORT", "8080")

# Online Stream and Download
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = False
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://shivam.dsrbotzz.workers.dev/")

# Admins, Channels & Users
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003243479334'))
LOG_CHANNEL_2 = int(environ.get('LOG_CHANNEL_2', '-1003453123686')) # Backup Log Channel ID
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1620169470 1065743814 695291232').split()]

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://Shivam:Shivam123@cluster0.2kweb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "techvjautobot")

# Shortlink Info
SHORTLINK = bool(environ.get('SHORTLINK', False)) # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')





