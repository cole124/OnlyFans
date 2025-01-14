import os
import time
import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.orm import scoped_session
from alembic.config import Config
from alembic import command
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import func
from database.databases.user_data import user_database


def create_database_session(
    connection_info, connection_type="sqlite:///", autocommit=False, pool_size=5
) -> tuple[scoped_session, Engine]:
    kwargs = {}
    if connection_type == "mysql+mysqldb://":
        kwargs["pool_size"] = pool_size
        kwargs["pool_pre_ping"] = True
        kwargs["max_overflow"] = -1
        kwargs["isolation_level"] = "READ COMMITTED"

    engine = sqlalchemy.create_engine(
        f"{connection_type}{connection_info}?charset=utf8mb4", **kwargs
    )
    session_factory = sessionmaker(bind=engine, autocommit=autocommit)
    Session = scoped_session(session_factory)
    return Session, engine


def create_mysql_database_session() -> tuple[scoped_session, Engine]:
    kwargs = {}
    # if connection_type == "mysql+mysqldb://":
    kwargs["pool_size"] = 5
    kwargs["pool_pre_ping"] = True
    kwargs["max_overflow"] = -1
    kwargs["isolation_level"] = "READ COMMITTED"

    queryObj={}
    if(not bool(os.environ.get('SQL_SSL_DISABLED',"False"))):
        queryObj["ssl_disabled"]=False
        queryObj["ssl_ca"]=os.environ.get('SQL_SSL_CA',"DigiCertGlobalRootCA.crt.pem")
    

    # kwargs["ssl"]={"ssl_ca":"DigiCertGlobalRootCA.crt.pem"}

    # sqlUrl = sqlalchemy.engine.url.URL(drivername="mysql+mysqlconnector",username=os.environ.get('SQL_USER','python'),password=os.environ.get('SQL_PASS', 'Jnmjvt20!'),host=os.environ.get('sqladd', 'shackleton-mysql.mysql.database.azure.com'),port=os.environ.get('sqlport', 3306),database=os.environ.get('SQL_DATABASE','vue_data'),query={"ssl_ca": "DigiCertGlobalRootCA.crt.pem"})
    sqlUrl = sqlalchemy.engine.url.URL(drivername="mysql+mysqlconnector",username=os.environ.get('SQL_USER','python'),password=os.environ.get('SQL_PASS', 'Jnmjvt20!'),host=os.environ.get('sqladd', 'shackleton-mysql.mysql.database.azure.com'),port=os.environ.get('sqlport', 3306),database=os.environ.get('SQL_DATABASE','vue_data'),query=queryObj)

    engine = sqlalchemy.create_engine(sqlUrl, **kwargs)

    # engine = sqlalchemy.create_engine(
    #     "mysql+mysqlconnector://{}:{}@{}:{}/{}?ssl=true".format(os.environ.get('SQL_USER','python'),os.environ.get('SQL_PASS', 'Jnmjvt20!'),os.environ.get('sqladd', 'shackleton-mysql.mysql.database.azure.com'),os.environ.get('sqlport', 3306),os.environ.get('SQL_DATABASE','vue_data')), **kwargs
    # )
    session_factory = sessionmaker(bind=engine, autocommit=True,autoflush=False)
    Session = scoped_session(session_factory)
    return Session, engine

def create_mssql_database_session() -> tuple[scoped_session, Engine]:
    kwargs = {}
    # if connection_type == "mysql+mysqldb://":
    kwargs["pool_size"] = 5
    kwargs["pool_pre_ping"] = True
    kwargs["max_overflow"] = -1
    kwargs["isolation_level"] = "READ COMMITTED"

    engine = sqlalchemy.create_engine(
        "mssql+pyodbc://{}:{}@{}/{}?driver=FreeTDS&port=1433&odbc_options='TDS_Version=8.0'".format(os.environ.get('SQL_USER','python'),os.environ.get('SQL_PASS', 'Jnmjvt20!'),os.environ.get('sqladd', '192.168.1.128'),os.environ.get('SQL_DATABASE','vue_data'))
    )
    session_factory = sessionmaker(bind=engine, autocommit=True,autoflush=False)
    Session = scoped_session(session_factory)
    return Session, engine


def run_revisions(alembic_directory: str, database_path: str = ""):
    while True:
        try:
            ini_path = os.path.join(alembic_directory, "alembic.ini")
            script_location = os.path.join(alembic_directory, "alembic")
            full_database_path = f"sqlite:///{database_path}"
            alembic_cfg = Config(ini_path)
            alembic_cfg.set_main_option("script_location", script_location)
            alembic_cfg.set_main_option("sqlalchemy.url", full_database_path)
            command.upgrade(alembic_cfg, "head")
            command.revision(alembic_cfg, autogenerate=True, message="content")
            break
        except Exception as e:
            print(e)
            print


def run_migrations(alembic_directory: str, database_path: str) -> None:
    while True:
        try:
            ini_path = os.path.join(alembic_directory, "alembic.ini")
            script_location = os.path.join(alembic_directory, "alembic")
            full_database_path = f"sqlite:///{database_path}"
            alembic_cfg = Config(ini_path)
            alembic_cfg.set_main_option("script_location", script_location)
            alembic_cfg.set_main_option("sqlalchemy.url", full_database_path)
            command.upgrade(alembic_cfg, "head")
            break
        except Exception as e:
            print(e)
            print

def FlushDatabase(database_session,cnt):
    cnt+=1
    try:
        database_session.flush()
    except Exception as inst:
        if cnt<=9:
            time.sleep(cnt*10)
            FlushDatabase(database_session,cnt)
        else:
            print(f"Unexpected error committing. Count: {cnt}", inst)

class database_collection(object):
    def __init__(self) -> None:
        self.user_database = user_database

    def database_picker(self, database_name):
        if database_name == "user_data":
            database = self.user_database
        else:
            database = None
            print("Can't find database")
            input()
        return database


def create_auth_array(item):
    auth_array = item.__dict__
    auth_array["support_2fa"] = False
    return auth_array


def get_or_create(session: Session, model, defaults=None, fbkwargs: dict = {}):
    fbkwargs2 = fbkwargs.copy()
    instance = session.query(model).filter_by(**fbkwargs2).one_or_none()
    if instance:
        return instance, True
    else:
        fbkwargs2 |= defaults or {}
        instance = model(**fbkwargs2)
        try:
            session.add(instance)
            session.commit()
        except IntegrityError:
            session.rollback()
            instance = session.query(model).filter_by(**fbkwargs2).one()
            return instance, False
        else:
            return instance, True


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
