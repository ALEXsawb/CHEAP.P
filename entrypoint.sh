#!/bin/bash

if [ "$SQL_DATABASE" = "CheapShopp" ]
then
    echo "Waiting for postgres..."
    echo $SQL_HOST

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

cd CheapSh0p
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata db.json
python manage.py test tests --verbosity=2


exec "$@"