#!/bin/bash

echo "start customer service...."
echo "django makemigrations..."
python manage.py makemigrations appPatient
echo "django migrate..."
python manage.py migrate
echo "run server..."
python manage.py runserver 0.0.0.0:8002
