# py_web_HW13_part1 (поетапна реалізація застосунку від дз11 до дз 13)
# почнемо з ДЗ11

1. poetry add fastapi uvicorn sqlalchemy psycopg2 alembic jinja2

2. створюємо структуру проєкту, db.py - підключення до БД, models.py - моделі, config.ini - дані для підключення

3. запускаємо докер, запускаємо дбивер, створюємо базу

4. alembic init migrations

5. migrstions/env.py
    from src.database.models import Base
    from src.database.db import URI

    # target_metadata = None
    target_metadata = Base.metadata
    config.set_main_option("sqlalchemy.url", URI)

6. alembic revision --autogenerate -m 'Init'
7. alembic upgrade head

8. src/schemas.py - Створюємо схеми валідації

9. Додаємо реалізацію маршрутів у файл main.py

10. src/routes/contacts.py - Роутери для модулів contacts містять точки доступу для операцій CRUD із контактами

11. src/repository/contacts.py - методи роботи бази даних із контактами

12. poetry add faker
    poetry add pydantic@^2.4.2 --extras "email"

13. src/database/models.py - заповнення бази(за аналогією з попередніх дз) треба додати poetry add faker

14. додаємо static/covers.css templates/index.html

15. запуск сервера:
    uvicorn main:app --reload

# ДЗ12

16. нам потрібно додати наступні пакети:
    poetry add python-jose["cryptography"] - (надає функціональність для роботи з JSON Web Tokens (JWT) та допомагає створювати безпечні токени аутентифікації та авторизації для REST API)
    poetry add passlib["bcrypt"] - (необхідний для хешування паролів користувачів. Хешування паролів необхідно, щоб їх не можна було відновити у вихідний вигляд, навіть, якщо дані витечуть з бази даних)
    poetry add python-multipart - (для роботи з файлами у форматі multipart/form-data, який є основним форматом для завантаження файлів по HTTP, необхідний у цьому випадку для правильної роботи FastAPI)
    poetry add libgravatar - (надає функціонал для взаємодії із Gravatar API. Gravatar - це сервіс, який дозволяє користувачам призначати своєму email-адресі глобальний аватар, який використовується на різних веб-сайтах. Libgravatar забезпечує простий спосіб отримання URL-адреси аватара для заданої email-адреси.)

17. Змінюємо моделі src/database/models.py додаємо новий class User(Base), додаємо в класс контакт:
        user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None)
        user = relationship("User", backref="notes")
    та робимо міграцію:
        alembic revision --autogenerate -m "add user"
        alembic upgrade heads

18. Додаємо схеми валідації. file: src/schemas.py (чотири моделі Pydantic: UserModel, UserDb, UserResponse та TokenModel)

19. Створюємо репозиторій користувача. file: src/repository/users.py
        get_user_by_email ця функція приймає email та сеанс бази даних db та повертає об'єкт користувача з бази даних, якщо він існує з такою адресою електронної пошти.
        create_user ця функція приймає параметр body, який вже пройшов валідацію моделлю користувача UserModel з тіла запиту, та другий параметр - сеанс бази даних db. Створює нового користувача у базі даних, а потім повертає щойно створений об'єкт User.
        update_token ця функція приймає об'єкт користувача user, токен оновлення token та сеанс бази даних db. Вона оновлює поле refresh_token користувача та фіксує зміни у базі даних.

20. Cтворюємо екземпляр класу auth_service = Auth(), який будемо використовувати у всьому коді для виконання операцій аутентифікації та авторизації.
        file: src/services/auth.py 

21. Маршрути аутентифікації. Створимо файл src/routes/auth.py

22. підключити новий роутер у головному файлі застосунку main.py
        from src.routes import contacts, auth

        app.include_router(contacts.router, prefix='/api')
        app.include_router(auth.router, prefix='/api')

23. Додаємо авторизацію src/repository/contacts.py
    У кожну функцію нашого репозиторію ми додаємо новий параметр user: User з поточним користувачем. І тепер, під час запитів, за допомогою методу filter(Tag.user_id == user.id) враховуємо належність тегу конкретному користувачеві.

24. Змінюємо маршрути. src/routes/contacts.py
    необхідно додати авторизацію за допомогою методу get_current_user класу Auth. Для кожного маршруту, де необхідна авторизація, потрібно додати параметр за допомогою залежності Depends(auth_service.get_current_user) Параметр current_user: User = Depends(get_current_user) отримує інформацію про поточного користувача з токена доступу access_token, який ми повинні надати разом із запитом до маршруту.

# ДЗ13

25. нам потрібно додати наступні пакети:
    poetry add fastapi-mail
    poetry add python-dotenv
    poetry add redis@4.2
    poetry add fastapi-limiter
    poetry add cloudinary

26. Змінюємо моделі та репозиторій​. В модель User необхідно додати поле confirmed = Column(Boolean, default=False)
    та робимо міграцію:
        alembic revision --autogenerate -m "upd models user"
        alembic upgrade heads

27. У репозиторії для роботи з даними користувача src/repository/users.py додамо наступну функцію.
    async def confirmed_email(email: str, db: Session) -> None:
        user = await get_user_by_email(email, db)
        user.confirmed = True
        db.commit()

28. Сервіс надсилання листів для верифікації. створюємо src/services/email.py змінюємо один рядок !!!! в такий формат MAIL_FROM="a.dorofeev_79@meta.ua"

29. Всередині сервісу Auth реалізуємо метод create_email_token
    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

30. Реалізуємо шаблон листа у файлі src/services/templates/email_template.html

31. Змінюємо роботу маршрутів​. Реєстрація користувача​ src/routes/auth.py
    В обробці маршруту реєстрації користувача "/signup" з’явився новий рядок коду: background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)

32. Аутентифікація користувача src/routes/auth.py
    Ми перевіряємо властивість user.confirmed, і якщо email не підтверджений – генеруємо виняток з описом "Email not confirmed"

33. Підтвердження email src/routes/auth.py
    Додамо новий маршрут /confirm email/{token} для реалізації підтвердження електронної пошти. 

34. Додамо реалізацію методу auth_service.get_email_from_token в src/services/auth.py
    додамо в імпорти from jose import JWTError, jwt

35. Повторне надсилання листа src/routes/auth.py 
        додамо в імпорти from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
        @router.post('/request_email')

36. Використання Docker Compose
    docker-compose.yml - з конспекту
    docker-compose up – запуск служб
    docker-compose down – зупинити і видалити контейнери

37. src/schemas.py
    class RequestEmail(BaseModel):
        email: EmailStr

38. додаємо пакет:
    poetry add pydantic-settings

39. вносимо зміни до src/schemas.py
    model_config = SettingsConfigDict(from_attributes=True)

40. створюємо файли .env та .env_example

41. створюємо файл src/conf/config.py

42. змінюємо підключення в db.py, змінюємо налаштування в docker-compose.yml
    в services/auth.py та email.py додаємо from src.conf.config import settings та змінюємо конф.дані за аналогією - MAIL_USERNAME="a.dorofeev_79@meta.ua", на MAIL_USERNAME=settings.mail_username,
    далі при додавані конф.даних треба це робити чере файл .env 

42. Додаємо обмеження до застосунку main.py:
    from fastapi_limiter import FastAPILimiter
    from fastapi_limiter.depends import RateLimiter
    import redis.asyncio as redis
    + зміни з конспекту

    А для маршруту встановити обмеження:
    src/routes/contacts.py

43. Cross-Origin Resource Sharing. main.py
    from fastapi.middleware.cors import CORSMiddleware

    origins = ["http://localhost:3000", "http://127.0.0.1:5000/"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],)

44. Збереження файлів у хмарі. додаемо дані підключення в .env та с config.py
    Розширимо наш клас Settingns новими змінними: src/conf/config.py
    визначимо новий роутинг /api/users та помістимо його у файл src/routes/users.py

    src/repository/users.py - async def update_avatar

    новий роутинг у файл main.py
    app.include_router(users.router, prefix='/api')