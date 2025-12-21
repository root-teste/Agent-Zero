# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define o arquivo do banco de dados local
SQLALCHEMY_DATABASE_URL = "sqlite:///./system.db"

# Cria a engine de conexão
# check_same_thread=False é necessário apenas para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria a sessão que será usada nas requisições
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos herdarem
Base = declarative_base()

# Função utilitária para obter o banco de dados (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
