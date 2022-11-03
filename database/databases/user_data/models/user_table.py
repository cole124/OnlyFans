### user_table.py ###

from datetime import datetime
from typing import cast

import sqlalchemy
from sqlalchemy.orm import declarative_base  # type: ignore

LegacyBase = declarative_base()


class user_table:
    __tablename__ = "users"
    __table_args__ = {
        'implicit_returning': False
    }
    
    # id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,autoincrement=True)
    userId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String(convert_unicode=True))
    subscription_price = cast(float, sqlalchemy.Column(sqlalchemy.DECIMAL))
    promo_price = cast(float, sqlalchemy.Column(sqlalchemy.DECIMAL))
    renewal_date = cast(datetime, sqlalchemy.Column(sqlalchemy.TIMESTAMP))
    subscribed = cast(bool, sqlalchemy.Column(sqlalchemy.Integer, default=0))
    Lists = sqlalchemy.Column(sqlalchemy.String)






    
