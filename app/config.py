class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # 使用 SQLite 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'  # 用于 session 加密等功能
