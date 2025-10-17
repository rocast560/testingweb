from typing import Union
from flask import request
from datetime import datetime

from app.database import get_db_connection

class User:
    def __init__(self, user_id: str, username: Union[str, None], role: Union[str, None]):
        self.__user_id = user_id
        self.__username = username
        self.__role = role

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def username(self) -> Union[str, None]:
        return self.__username
    
    @property
    def role(self) -> Union[str, None]:
        return self.__role
    
    @property
    def is_admin(self) -> bool:
        return self.__role == 'admin'
    

def get_user() -> Union[User, None]:
    session_id = request.cookies.get("session_id", None)

    if session_id is None:
        return None
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    u.user_id, u.username, s.expiration, u.role
                FROM
                    sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE
                    s.session_id = %s
                ORDER BY
                    s.expiration DESC LIMIT 1
                """,
                (session_id,)
            )
            result = cur.fetchone()

            if result is None:
                return None
            
            user_id, username, expiration, role = result

            if expiration < datetime.now():
                return None
            
            return User(user_id, username, role)
