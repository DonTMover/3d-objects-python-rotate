import os

# Ports (host side). Use docker-compose .env to override.
WEB_PORT = int(os.getenv('WEB_PORT', '8000'))
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', '3000'))
CADDY_PORT = int(os.getenv('CADDY_PORT', '8080'))

# Caddy host inside compose network
CADDY_HOST = os.getenv('CADDY_HOST', 'caddy')

# Default WEBAPP_URL (used by bot if WEBAPP_URL not set)
WEBAPP_URL = os.getenv('WEBAPP_URL', f'http://{CADDY_HOST}:{CADDY_PORT}/')
