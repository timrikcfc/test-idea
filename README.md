Процесc запуска проекта:

1. git clone https://github.com/timrikcfc/test-idea
2. python -m venv venv
3. source venv/bin/activate
4. pip install -r requirements.txt
5. python manage.py migrate
6. python manage.py createcachetable
7. python manage.py runserver


Запуск тестов:

python manage.py test resizeimg
