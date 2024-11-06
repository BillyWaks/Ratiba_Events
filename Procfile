release: python django-postgres/manage.py migrate --noinput
web: sh -c 'cd django-postgres && exec gunicorn ratiba.wsgi:application --log-file -'
