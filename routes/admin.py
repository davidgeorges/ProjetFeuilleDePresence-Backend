from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.promo import PromoInDb
from classes.Mail import mail
from models.user import UserInDB
from config.hashPassword import get_password_hash
from config.generatePassword import generate_password
from classes.Database import database
from classes.Error import error as errorLogger

"""
File containing admin routes.
@Author : David GEORGES
"""

admin = APIRouter()

#Create an user linked to a promo
@admin.post('/createAnUser', response_model=UserInDB)
async def create_an_user(user_receive: UserInDB = Body(...)):
    db = database.get_db()

    try:
        #Convert pydantic model to a Dict
        user = jsonable_encoder(user_receive)

        promo = await db["promo"].find_one({"_id": user["promo_id"]})

        if promo is None:
            return JSONResponse(content=f"Promo doesn't exist --> {user['promo_id']} - for --> {user['email']}",status_code=status.HTTP_200_OK)

        if await db["users"].find_one({"email": user["email"]}) is not None:
            return JSONResponse(content=f"User already in db for --> {user['email']} for promo --> {promo['promo_name']}",status_code=status.HTTP_200_OK)

        password_generate = generate_password()
        user["hashed_password"] = get_password_hash(password_generate)
        await db["users"].insert_one(user)
        mail.send_login_info(user["email"], password_generate)

        if user["role_id"] == "1":
            promo["student_list"].append(user["_id"])
        else:
            promo["teacher_list"].append(user["_id"])
        await db["promo"].update_one({"_id": promo["_id"]}, {"$set": promo})

        return JSONResponse(content="User registred with success.",status_code=status.HTTP_201_CREATED)

    except Exception as error :
        errorLogger.write_in_file("createAnUser : "+str(error))
        return JSONResponse(content="",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Create an promo
@admin.post('/addAnPromo')
async def add_an_promo(promo_receive: PromoInDb = Body(...)):
    try:
        promo = jsonable_encoder(promo_receive)
        if not await database.get_db()["promo"].find_one({"promo_name": promo["promo_name"]}): 
            await database.get_db()["promo"].insert_one(promo)
            return JSONResponse(content="Promo add with success.",status_code=status.HTTP_201_CREATED)
        return JSONResponse(content=f"Promo already in db for --> {promo['promo_name']}",status_code=status.HTTP_200_OK)
    except Exception as error :
        errorLogger.write_in_file("addAnPromo : "+str(error))
        return JSONResponse(content="",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



