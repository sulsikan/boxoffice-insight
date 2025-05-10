#!/bin/bash
cd /home/ec2-user/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정 (예: DB, SECRET_KEY)
export DJANGO_SETTINGS_MODULE=boxoffice.settings

# 마이그레이션 및 collectstatic (이미 됐더라도 안정 차원에서 재수행)
python manage.py migrate
python manage.py collectstatic --noinput

# 서버 실행
gunicorn boxoffice.wsgi:application --bind 0.0.0.0:8000 --daemon
