release: python manage.py makemigrations --no-input && python manage.py migrate --no-input
python manage.py collectstatic --noinput
web: gunicorn ratiba.wsgi