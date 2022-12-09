from typing import List
from pydantic import BaseModel,Field,StrictStr, validator
from bson import ObjectId
from models.pyObject import PyObjectId

"""
File containing  promo models.
@Author : David GEORGES
"""

#PromoBase data used through the application
class PromoBase(BaseModel):    
    promo_name : StrictStr
    promo_year : StrictStr

    @validator('promo_name')
    def promo_name_check(cls, v):
        if(len(v) >=1 and len(v) <= 24 ) : return v.lower()
        raise ValueError("promo_name require a minimmum of 1 and a maximum of 24 characters.")

    @validator('promo_year')
    def promo_year_check(cls, v):
        if(len(v) >=1 and len(v) <= 9 ) : return v.lower() 
        raise ValueError("promo_year require a minimmum of 1 and a maximum of 9 characters.")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

#PromoBase store in the db (at creation)
class PromoInDb(PromoBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    student_list : List[str]
    teacher_list : List[str]
    daily_token : str
    daily_teacher_id : str

    @validator('student_list')
    def status_id_check(cls, v):
        if v :
            raise ValueError("At promo creation student_list have to be empty.")
        return v

    @validator('teacher_list')
    def teacher_list_check(cls, v):
        if v :
            raise ValueError("At promo creation teacher_list have to be empty.")
        return v

    @validator('daily_token')
    def daily_token_check(cls, v):
        if v :
            raise ValueError("At promo creation daily_token have to be empty.")
        return v

    @validator('daily_teacher_id')
    def daily_teacher_id_check(cls, v):   
        if v :
            raise ValueError("At promo creation daily_teacher_id have to be empty.")
        return v


    
    