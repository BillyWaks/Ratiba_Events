release: python django-postgres/manage.py makemigrations --no-input
release: python django-postgres/manage.py migrate --no-input
# release: python django-postgres/manage.py collectstatic --no-input

web: gunicorn django-postgres.ratiba.wsgi
