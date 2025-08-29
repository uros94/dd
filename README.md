## instalation

### clone the project
- git clone https://github.com/uros94/dd.git
- cd dd

### setup python3.7 - the dependencies rely on it
- sudo apt update
- sudo apt install --reinstall python3-apt
- sudo apt install python3.7 python3.7-venv python3.7-dev

### setup venv
- python3.7 -m venv venv
- source venv/bin/activate
- pip install --upgrade pip setuptools wheel

### install requirenments
- pip install -r req.txt
- pip install django-background-tasks
- pip install django-multiselectfield
- python -m pip install Pillow

### comment out the background_task class !!!

- python manage.py makemigrations
- python manage.py migrate

### remove the comments from background_task class and run migrations again
- python manage.py makemigrations
- python manage.py migrate

### run the app
- python manage.py createsuperuser
- python manage.py runserver


### hit http://127.0.0.1:8000/test/ to populate the test db
