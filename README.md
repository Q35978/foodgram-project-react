# Описание проекта YaMDb


## Описание
Проект Foodgram - это сайт на котором пользователь может публиковать рецепты, 
добавлять их в "Избранное", подписываться на других пользователей и  скачивать
список продуктов, необходимых для приготовления выбранных блюд.

# Настройка необходимых файлов

```
# СУБД, с которой работаем
DB_ENGINE=django.db.backends.postgresql
# Имя базы данных
DB_NAME=
# Имя пользователя для подключения к базе данных
POSTGRES_USER=
# Пароль пользователя 
POSTGRES_PASSWORD=
# Название контейнера
DB_HOST=
# порт для подключения к БД
DB_PORT=
# Ключ приложения (по желанию)
SECRET_KEY=
```

# Нелбходимые для установки приложения команды
В Linux все команды необходимо выполнять от имени администратора

- Выполнить вход на удаленный сервер
- Установить docker:
```
sudo apt install docker.io 
```
- Установить docker-compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Отредактировать файл nginx.conf (infra/nginx.conf), обязательно в server_name вписать IP-адрес сервера
- Перенести файлы docker-compose.yml, nginx.conf на удаленныйсервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- собрать и запустить контейнеры на сервере:
```
docker-compose up -d --build
```
- Создать .env файл по предлагаемому выше шаблону. Обязательно изменить значения POSTGRES_USER и POSTGRES_PASSWORD
- Для работы с Workflow добавить в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<ключ приложения>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    USER=<имя пользователя для подключения к серверу где будет разворачиваться приложение>
    HOST=<IP сервера>
    SSH_KEY=<ваш SSH ключ для подключения к удаленному серверу>
    PASSPHRASE=<ключевая фраза для ssh rключа>
  
    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
- Когдасборка прошла успешно необходимо выполнить следующие действия (только при первом деплое):
    * провести миграции:
    ```
    docker-compose exec backend python manage.py migrate
    ```
    * Создать суперпользователя для первого входа:
    ```
    docker-compose exec backend python manage.py createsuperuser
    ```
    * Заполнить список ингридиентов:
    ```
    docker-compose exec backend python manage.py load_ingredients_from_csv
    ```

# Стек технологий
- Python
- Django REST framework
- PostgreSQL
- Gunicorn
- nginx
- Docker
- Git



