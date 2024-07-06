Для развёртывания проекта нуджно
1. Клонировать репозиторий

2.Установить докер

3. В директории 'backend' создать файл .env вида:

POSTGRES_PASSWORD = 'пароль от базы данных'
POSTGRES_USER = 'имя root пользователя бд'
POSTGRES_DB = 'название бд'
USER_AGENT = 'ваш USER_AGENT'

4. В директории 'frontend' создать файл .env вида:

BOT_TOKEN = 'токен вашего бота'

5. Далее сорбрать и зауптить проек с помощью команд:

docker compose build
docker compose up