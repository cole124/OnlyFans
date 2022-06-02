### messages.py ###

import copy
import datetime
from typing import cast

import sqlalchemy
from database.databases.user_data.models.api_table import api_table
from database.databases.user_data.models.media_table import \
    template_media_table
from database.databases.user_data.models.user_table import user_table
from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer

Base = declarative_base()
LegacyBase = declarative_base()


# class user_table(api_table,Base):
#     api_table.__tablename__ = "user_table"


class stories_table(api_table, Base):
    api_table.__tablename__ = "stories_temp"


class posts_table(api_table, Base):
    api_table.__tablename__ = "posts_temp"


class messages_table(api_table, Base):
    api_table.__tablename__ = "messages_temp"
    user_id = cast(int, sqlalchemy.Column(sqlalchemy.Integer))

    class api_legacy_table(api_table, LegacyBase):
        pass


class users_table(user_table,Base):
    pass

class media_table(template_media_table, Base):
    class media_legacy_table(template_media_table().legacy_2(LegacyBase), LegacyBase):
        pass


def table_picker(table_name, legacy=False):
    if table_name == "Stories":
        table = stories_table
    elif table_name == "Posts":
        table = posts_table
    elif table_name == "Messages":
        table = messages_table if not legacy else messages_table().api_legacy_table
    elif table_name == "Users":
        table = users_table
    else:
        table = None
        input("Can't find table")
    return table
