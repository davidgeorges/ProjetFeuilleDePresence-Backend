from motor.motor_asyncio import AsyncIOMotorClient
from config.config import settings
from classes.Error import error

"""
Database file.
@Author : David GEORGES
"""

class Database : 

    #private members
    __client = None
    __db = None

    def __init__(self,dbUrl,dbName):
        try : 
            self.__client = AsyncIOMotorClient(dbUrl)
            self.__db = self.__client[dbName]
        except Exception as e : 
            error.write_in_file("Error while connecting to database --> "+str(e))

    def get_db(self):
        return self.__db        
            
database = Database(settings.DB_URL,settings.DB_NAME)
