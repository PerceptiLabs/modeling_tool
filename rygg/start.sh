python wait-for-db.py || { exit 1; }
python -m django migrate --database=${DB} --settings rygg.settings
DJANGO_DATABASE=${DB} python -m django runserver 0.0.0.0:8000 --settings rygg.settings
