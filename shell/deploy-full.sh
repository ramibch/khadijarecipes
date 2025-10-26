git pull
uv run manage.py migrate
uv run manage.py compilemessages
uv run manage.py collectstatic --noinput
sudo systemctl restart huey_kh.service
sudo systemctl restart gunicorn_kh.service
