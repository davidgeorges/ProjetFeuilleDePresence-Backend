import time
from config.config import settings
from jose import jwt
from datetime import datetime, timedelta

"""
Token file.
@Author : David GEORGES
"""


class Token:

    # private members
    __token_error = " "

    # Get an data from token
    def get_data(self, data_to_get, token_receive,token_type):
        if "Bearer " in token_receive :
            token = token_receive.replace("Bearer ", "")
            try:
                if token_type == "access" :
                    decode_token = jwt.decode(token, settings.JWT_ACCESS_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM])
                elif token_type == "refresh" :
                    decode_token = jwt.decode(token, settings.JWT_REFRESH_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM])
                    print(decode_token.get(data_to_get))
                return decode_token.get(data_to_get)
            except Exception as e:
                self.set_token_error(
                    "No access - Error while decoding token " + data_to_get +" --> "+str(e))
        else : 
            self.set_token_error("Not valid - Missing bearer")

    # Check if the token has expired
    def check_if_is_expired(self, token_receive,token_type):
        if "Bearer " in token_receive :
            token = token_receive.replace("Bearer ", "")
            try:
                if token_type == "access" :
                    decode_token = jwt.decode(token, settings.JWT_ACCESS_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM])
                elif token_type == "refresh" :
                    decode_token = jwt.decode(token, settings.JWT_REFRESH_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM])
                try:
                    return "OK" if decode_token.get("exp") >= time.time() else self.set_token_error("Expired token")
                except:
                    self.set_token_error("Not valid token - Expired missing")
            except Exception as e:
                self.set_token_error("JWT Error --> "+str(e))
                return False
        else : 
            self.set_token_error("Not valid - Missing bearer")

    # Create token with id and role and expire time
    def create_token(self, id_receive, role_receive, token_type):
        try:
            if token_type == "access" :
                return jwt.encode({
                "id": id_receive,
                "role": role_receive,
                "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_IN)
                }, settings.JWT_ACCESS_TOKEN_SECRET, settings.JWT_ALGORITHM)
            elif token_type == "refresh" :
                return jwt.encode({
                "id" : id_receive,
                "role" : role_receive ,
                "exp" : datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRES_IN)
                }, settings.JWT_REFRESH_TOKEN_SECRET,settings.JWT_ALGORITHM)
        except Exception as e :
            self.set_token_error("Error while creating user token --> "+str(e))
            return False

    # GETTER & SETTER
    def set_token_error(self,error_message):
        self.__token_error = error_message

    def get_token_error(self):
        return self.__token_error 
    
token = Token()