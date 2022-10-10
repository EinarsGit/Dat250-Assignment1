from flask_login import UserMixin
from app import secure_query

from app import login_manager


class User(UserMixin):
    def __init__(self, username, password, id=0, first_name=None, last_name=None, education=None,
                 employment=None, music=None, movie=None, nationality=None, birthday=None):
        self.__id = id
        self.__username = username
        self.__password = password
        self.__first_name = first_name
        self.__last_name = last_name
        self.__education = education
        self.__employment = employment
        self.__music = music
        self.__movie = movie
        self.__nationality = nationality
        self.__birthday = birthday

    def get_id(self):
        return self.__username

    def get_password(self):
        return self.__password


def get_user_by_name(username):
    try:
        query = secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)
        user = User(username=query['username'], password=query['password'], id=query['id'],
                    first_name=query['first_name'],
                    last_name=query['last_name'], education=query['education'], employment=query['employment'],
                    music=query['music'], movie=query['movie'], nationality=query['nationality'],
                    birthday=query['birthday'])
        return user

    except TypeError:
        return None
    except:
        return None


@login_manager.user_loader  # importing the login manager
def load_user(username):
    return get_user_by_name(username)
