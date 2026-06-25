#!/bin/bash
set -e

APP_NAME="atc"
DOMAIN="atc.codegraphics.co.tz"
APP_DIR="/opt/apps/$DOMAIN"
CADDY_EMAIL="admin@codegraphics.co.tz"

echo "=== Deploying $APP_NAME to $DOMAIN ==="

# 1. Create directory structure
sudo mkdir -p $APP_DIR
sudo chown -R $(whoami):$(whoami) $APP_DIR

# 2. Clone/pull code
if [ -d "$APP_DIR/.git" ]; then
  cd $APP_DIR && git pull
else
  git clone git@github.com:nasrtechindustry/atc.git $APP_DIR
fi

cd $APP_DIR

# 3. Create .env if not exists
if [ ! -f .env ]; then
  cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
DATABASE_URL=postgres://atc:\${DB_PASSWORD}@db:5432/atc
DB_PASSWORD=$(openssl rand -hex 12)
EOF
fi

# 4. Build and start
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 5. Run migrations and collectstatic
docker compose -f docker-compose.prod.yml exec -T app python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec -T app python manage.py collectstatic --noinput

# 6. Set up Caddy
sudo tee /etc/caddy/Caddyfile > /dev/null << EOF
{
	email $CADDY_EMAIL
}

$DOMAIN {
	reverse_proxy /static/* 127.0.0.1:10204
	reverse_proxy /media/* 127.0.0.1:10204
	reverse_proxy 127.0.0.1:10204
}

realtime.$DOMAIN {
	reverse_proxy 127.0.0.1:10203
}

www.$DOMAIN {
	redir https://$DOMAIN{uri}
}
EOF

sudo systemctl reload caddy

echo "=== Deploy complete ==="
echo "Site: https://$DOMAIN"
echo "Admin: https://$DOMAIN/admin/"
echo "Realtime: ws://realtime.$DOMAIN"
