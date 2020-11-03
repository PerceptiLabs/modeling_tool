python wait-for-db.py || { exit 1; }
python manage.py migrate --database=${DB}
DJANGO_DATABASE=${DB} python manage.py runserver 0.0.0.0:8000
