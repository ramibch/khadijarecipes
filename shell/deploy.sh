git pull
uv run manage.py migrate
uv run manage.py compilemessages
sudo systemctl restart huey_khadijarecipes.service
sudo systemctl restart gunicorn_khadijarecipes.service
