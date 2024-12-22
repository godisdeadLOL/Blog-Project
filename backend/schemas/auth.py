from pydantic import BaseModel


class RegisterForm (BaseModel) :
    username : str
    password : str