# CHEAP.P


**CHEAP.P** - educational project, online store, The project provides convenience to 
the intermediary in the implementation of retail trade without intermediate storage 
goods in your warehouse through the database structure and admin panel. The 
convenience of the user lies in the convenient and intuitive structure of the site
An API is also provided for further development of the project, its scaling and
replication

<br>
<br>


### Navigation
***
* [Launch]()
  * [standard](#standard)
  * [using docker-compose](#docker)
* [Go to site](#go_to_site)
* More about the project
  * [Ukrainian language](#more_about_project_UA)
  * [English language](#more_about_project_EN)
***
<br>
<br>



Launch
---



#### Standard<a name="standard"></a>
___

Before starting, you must check for the existence of a virtual environment or create one if necessary.
If you are use Linux then you need write `python` or `python3` before commands listed below
In the directory with `requirements.txt` need running
``` 
pip install -r requirements.txt
```

In the directory CheapSh0p, where is `manage.py` need running
```
manage.py makemigrations
manage.py migrate
manage.py loaddata db.json
manage.py runserver
```

For check workable you can launch tests 
```
manage.py test
```
<br>
<br>
<br>

#### Docker-compose<a name="docker"></a>
___
Before using docker, you must be Docker Desktop running
In directory with docker-compose.yml need to run
```
docker-compose up --build
```

For stop container, you need to run `Ctrl+C` or 
```
docker-compose stop
```

For renewal him, you need run
```
docker-compose up
```

For delete container with volumes and image, you need to run
```
docker-compose down --volumes --rmi local
```

To access the container's bash you need to run
```
docker-compose exec -it chp_shp bash
```
Inside which you can, for example, call the Django shell
To get started you need be to the directory with manage.py
```
cd CheapSh0p
python manage.py shell
```
To exit from Django Shell you need use `quit()`

<br>
<br>

Go to site<a name="go_to_site"></a>
---
Next, follow the path http://localhost:8000/
<br>
<br>
<br>

Більше про проект<a name="more_about_project_UA"></a>
---

### Cache
У проекті використовується кешування сторінок, частин шаблонів, 
та об'єктів, з метою оптимізації кількості запистів до БД, та 
ітогового часу відповіді користовачу.


### Middleware
У проекті використовується додаткове, проміжне ПЗ(`middleware`). 
Ми маємо дві варіації проміжного ПЗ: `MiddlewareForAddingViews`.

Його завдання - збільшення кількості переглядів продуктів та колекцій, 
під час додавання переглядів до продукту відбувається те ж саме, й до 
типу одягу.


### MultiForm & FormSet

На сторінці кошика використовуються як MultiForm у вигляді 
MultiModelForm, так і FormSet. Ідея була у створенні та 
об'єднанні набору форм замовленя з формою доставки. 
Рішення, використання такого методу формування сторінки, було 
прийнято винятково у навчальних цілях, метою яких були 
використання ідей сторонніх людей, та їх оптимізація з метою
не дійти до оновлення сторінки при зміні кількости 
одиниць товару.


### API
API створено з метою масштабування та теражування.
У API є розподіл прав доступу. Користувачі мають лише доступ 
до перегляду данних, користуючись лише безпечними методами 
запросів, натомість персонал має змогу редагувати або видаляти вже 
існуючі товари, колекції, типи.

Доступна аутентифікація на основі сесій, або токенів.
Також присутня пагінація, по 5 одиниць на сторінку.

Кількість запитів до БД з правами користувача оптимізована,
натомість кількість запитів з правами персоналу оптимізована 
частково.
Також на API не розповсюджується кешування та проміжне ПЗ, що
стосується переглядів.


### SuperUser

При використанні `db.json` для завантаження даних до БД, 
буде завантажений також й `superuser` з ім'ям користувача 
'NewUser' та паролем 'NewUser12345'.

---
##### Більше інформації про проект буде надано пізніше, наразі у вас є можливість ознайомитись з ним, та дізнатись деталі аналізуючи сам проект
<br>
<br>
<br>
<br>
<br>
<br>


More about the project <a name='more_about_project_EN'></a>
---


### Cache
The project uses caching pages, parts of templates and objects. 
All these to optimize the quantity queries to DB and total response time


### Middleware
The project uses additional `middleware`,this is `MiddlewareForAddingViews`.

Their task is to add views to a product or collection. Important, when a user gets to the 
product page, then `middleware` add views of the product and its type of clothing. 


## MultiForm & FormSet
On the basket page use MultiModelForm and FormSet. Idea was to create and unite set 
orderforms with delivery form. This method page formation used for exclusively for 
educational goals. This is someone else's idea with my optimization, the goal of 
which was to create conditions close to real


### API
The API is designed to scale and replicate. The API has permissions allocation. 
Users only have access to view data using only secure query methods. instead, 
staff can edit or delete existing products, collections, type of clothing.

Session-based or token-based authentication is available
There is also pagination, 5 units per page.


With user access, we have the most optimized number of database queries.
But, the quantity of requests with staff permission had partially optimized
Caching and custom middleware haven't effect to API


### SuperUser
When we use `db.json` for load data into the DB(this also happens in the
container, when we use docker-compose), then we load and data about `superuser`
This `superuser` has name 'NewUser' and password 'NewUser12345'


---
##### More information about project will be added later. Now you can familiarize yourself with the project, learn more details
