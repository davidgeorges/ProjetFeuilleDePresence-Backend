from pydantic import BaseModel, validator

"""
File containing role models.
@Author : David GEORGES
"""

#User data used through the application
class RoleBase(BaseModel):    
    role_name : str

    @validator('role_name')
    def role_name_check(cls, v):
        if(len(v) >=1 and len(v) <= 24 ) :
            assert v.isalpha() , "Only alphabet characters are accepted in role_name field."
        else : 
            raise ValueError("role_name require a minimmum of 1 and a maximum of 24 characters.")
        return v.lower()

#User store in the db (at creation)
class RoleInDb(RoleBase):
    id : str

    @validator('id')
    def role_id_check(cls, v):
        if(len(v) !=1 ) :
            assert v.isalpha() , "Only alphabet characters are accepted in role_id field."
        else : 
            raise ValueError("role_id require a minimmum and maximum of 1 characters.")
        return v.lower()
