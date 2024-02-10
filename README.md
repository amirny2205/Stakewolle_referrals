# Stakewolle_referrals
выполнение вот этого тестового:
https://docs.google.com/document/d/1Ts4ZfUOLDMJcVwlyK6HKhb8PyIyS2TqE/edit?usp=sharing&ouid=105455195895039400119&rtpof=true&sd=true
## описание запуска сервиса:
сервис разрабатывался на postgres, поэтому пишу инструкцию для него

заходим в постгрес:
```
su - postgres
psql
```
создаем дб:
```
CREATE DATABASE stakewolle_referrals_db;
```
выходим из шелла psql и шелла с юзером postgres:
```
exit
exit
```
создаём и активируем виртуальную среду, на линуксе это:
```
python3 -m venv venv
source ./venv/bin/activate
```
устанавливаем необходимые пакеты питона:
```
pip install -r requirements.txt
```
создаём .env файл по типу того, что указано в .env_example

настройка сервиса email указана в следующем заголовке


проводим миграцию:
```
./manage.py migrate
```
на данном этапё всё должно работать:
```
./manage.py runserver
```
### настройка сервиса отправки email
в settings.py вам нужно работать со следующими параметрами, сейчас они настроены для mail.ru:
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
```
будьте осторожны: у разных провайдеров отличаются настройки `EMAIL_USE_SSL` и `EMAIL_USE_TLS`

в файле .env для отправки сообщений необходимо указать `EMAIL_HOST_USER` и `EMAIL_HOST_PASSWORD`, настройки для smtp, способ их получения у разных провайдеров разный. Можно не указывать, отправка емейла задаётся явно, он укажет на ошибку, если таковая есть.

## описание работы сервиса; swagger
для докуметации по эндпоинтам используется пакет drf-spectacular(одна
из реализаций swagger)

документация swagger доступна по умолчанию на
`http://127.0.0.1:8000/api/schema/swagger-ui/`

если вы обновили код, необходимо обновить и структуру, сгенерированную swagger'ом:
```
./manage.py spectacular --color --file schema.yml
```


### краткий гайд по работе с сервисом:

создаём пользователя

`POST http://127.0.0.1:8000/auth/users/`

в теле запроса передаём:

`{"username": "tmp_user_25", "password": "tmppassword2000!", "email": "your_real_email@wewilltestit.ru"}`


затем генерируем JWT-токен

`POST http://127.0.0.1:8000/auth/jwt/create`

в теле передаём:

`{"username": "tmp_user_25", "password":"tmppassword2000!"}`


полученный access_code используем как Bearer в последующих действиях,
например, в "postman" это делается во вкладке "Authorization"


генерируем реферральный код:

`POST http://127.0.0.1:8000/my_referral_codes/`

в теле передаём:

`{"expiry_date":"2024-03-08T12:33:01Z", "send_mail": false}`

если отправка емейла настроены в .env и в settings.py,
можно проставить `"send_mail": true`


получаем реферральный код, например

`{"code_str":"rjoqnylipzntnxfzwhfcbaiskwuetxlsekzducwziwmoefpxicaeaortbtuzouue","active":true,"expiry_date":"2024-03-08T12:33:01Z","user":17}`



далее можно:

получить, отредактировать или удалить реферральный код по эндпоинту
`http://127.0.0.1:8000/my_referral_codes/{code_str}` , используя
запросы GET, PUT, PATCH(в этом случае необходимо в теле запросы передать
`"partial": "true"`), DELETE



при изменении значения поля "active" любого из кодов юзера на true,
остальные коды сбрасываются на "false", и регистрация по ним будет
невозможна(вылезет соответствующая ошибка)



далее можно зарегистрировать нового пользователя по существующему
активному реферральному коду:

`POST http://127.0.0.1:8000/auth/users/`

в теле передаём:

`{"username": "tmp_user_26", "password": "tmppassword2000!", "email":
"my_email@yandex.ru", "referral_code_for_registration":
"rjoqnylipzntnxfzwhfcbaiskwuetxlsekzducwziwmoefpxicaeaortbtuzouue"}`



по любому JWT-токену на эндпоинте POST `http://127.0.0.1:8000/referrals_by_id/` мы увидим, соответственно, пользователей, которые зарегистрировались по одному из реферральных кодов пользователя, которого передаем в теле запроса(`{"id": 17}`):


`[ { "email": "my_email@yandex.ru", "id": 18, "username": "tmp_user_26" } ] `
