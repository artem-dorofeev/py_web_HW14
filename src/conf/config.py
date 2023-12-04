from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_port: int = 5232
    sqlalchemy_database_url: str ="postgresql+psycopg2://username:password@localhost:5432/db_name"
    secret_key: str = "secret key"
    algorithm: str = "algotihtm"
    mail_username: str = "example@meta.ua"
    mail_password: str = "password"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = "localhost"
    redis_port: int = 6379
    cloudinary_name: str = "cloudinary"
    cloudinary_api_key: str = "cloudinary"
    cloudinary_api_secret: str = "cloudinary"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()