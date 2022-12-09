from typing import Dict
from pydantic import BaseModel,Field,EmailStr, StrictStr,validator
from bson import ObjectId
from models.pyObject import PyObjectId

"""
File containing user models.
@Author : David GEORGES
"""

#Serves as a base for the other models
class UserBase(BaseModel):     
    email: EmailStr
    last_name :str
    first_name :str
    
    #All validator
    @validator('email')
    def email_check(cls, v):
        return v.lower()

    @validator('last_name')
    def last_name_check(cls, v):
        if(len(v) >=1 and len(v) <= 24 ) :
            assert v.isalpha() , "Only alphabet characters are accepted in last_name field."
        else : 
            raise ValueError("last_name require a minimmum of 1 and a maximum of 24 characters.")
        return v.lower()

    @validator('first_name')
    def first_name_check(cls, v):   
        if(len(v) >=1 and len(v) <= 24 ) :
            assert v.isalpha() , "Only alphabet characters are accepted in first_name field."
        else : 
            raise ValueError("first_name require a minimmum of 1 and a maximum of 24 characters.")
        return v.lower()
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

#User data during the connection
class UserIn(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def password_check(cls, v):   
        if(len(v) == 0 ) :
            raise ValueError("Enter a password")
        else : 
            return v
            
#User store in the database (registration)
class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    status : Dict
    role_id: StrictStr
    promo_id : StrictStr
    refresh_token : str

    #All validator
    @validator('hashed_password')
    def hashed_password_check(cls, v):
        if v :
            raise ValueError("At user creation hashed_password have to be empty.")
        return v

    @validator('role_id')
    def role_id_check(cls, v):   
        if(v == "1" or v == "2" ) : 
            return v
        else : 
            raise ValueError("Can create only an account for student and teacher.")
        

    @validator('status')
    def status_check(cls, v):
        if v :
            raise ValueError("At user creation status_id have to be empty.")
        return v

    @validator('promo_id')
    def promo_id_check(cls, v):   
        if(len(v) != 24) :
            raise ValueError("Wrong promo_id, id are fixed at 24 characters")
        return v.lower()

    
