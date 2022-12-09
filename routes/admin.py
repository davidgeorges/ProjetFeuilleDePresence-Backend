from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.promo import PromoInDb
from classes.Mail import mail
from models.user import UserInDB
from config.hashPassword import get_password_hash
from config.generatePassword import generate_password
from classes.Database import database
from classes.Error import error

"""
File containing admin routes.
@Author : David GEORGES
"""

admin = APIRouter()

#Create an user linked to a promo
@admin.post('/createAnUser', response_model=UserInDB)
async def create_an_user(user_receive: UserInDB = Body(...)):

    db = database.get_db()

    #Init status code & content
    status_code = 500
    detail = " "

    try : 
        #Convert pydantic model to a Dict
        user = jsonable_encoder(user_receive)
        try : 
            #Get the promo by id
            promo = await db["promo"].find_one({"_id": user["promo_id"]})
            #If the promo exist
            if promo is not None:
                try:         
                    #Check if the user doesn't already exist in the db 
                    if ( await db["users"].find_one({"email": user["email"]})) is None:
                        #Generate the user password
                        password_generate = generate_password()
                        #Hash the user password generated
                        user["hashed_password"] = get_password_hash(password_generate)
                        try:
                            #Write the user in database
                            await db["users"].insert_one(user)
                            try:
                                #Send user mail with password
                                mail.send_login_info(user["email"], password_generate)
                                #Update the promo student_list or teacher_list
                                if(user["role_id"] == "1") : 
                                    promo["student_list"].append(user["_id"])
                                else : 
                                    promo["teacher_list"].append(user["_id"])
                                try:
                                    #Update the promo in database
                                    await db["promo"].update_one({"_id":promo["_id"]},{"$set":promo})
                                    return JSONResponse("User registred with success.", status.HTTP_201_CREATED)
                                except Exception as e :  
                                    detail = f"Error while updating promo --> {promo['promo_name']} for  user --> {user['email']} --> "+str(e)
                            except Exception as e : 
                                detail = f"Error while sending user mail for --> {user['email']} for promo --> {promo['promo_name']} --> "+str(e)  
                        except Exception as e : 
                            detail = f"Error while writting user in db for --> {user['email']} for promo --> {promo['promo_name']} --> " +str(e)
                    else:
                        status_code = 200
                        detail= f"User already in db for --> {user['email']} for promo --> {promo['promo_name']}"
                except Exception as e : 
                    detail= f"Error while getting user from db for --> {user['email']} for promo --> {promo['promo_name']} --> "+str(e) 
            else :
                status_code = 200
                detail = f"Promo doesn't exist --> {user['promo_id']} - for --> {user['email']}"
        except Exception as e : 
            detail = "Error while getting the promo by id --> "+str(e)
    except Exception as e : 
       detail =  "Error while convert pydantic to dict --> "+str(e)
    
        
    try :
        error.write_in_file(detail)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))

    raise HTTPException(status_code,detail)


#Create an promo
@admin.post('/addAnPromo')
async def add_an_promo(promo_receive : PromoInDb = Body(...)):

    db = database.get_db()

    #Init status code & content
    status_code = 500
    detail = ""

    try : 
        #Convert pydantic model to a Dict
        promo = jsonable_encoder(promo_receive)
        try:
            #Check if promo already exist 
            if await db["promo"].find_one({"promo_name": promo["promo_name"]}) == None :
                try :
                    #Write the promo in database
                    await db["promo"].insert_one(promo)
                    return JSONResponse("Promo add with success.",status.HTTP_201_CREATED)
                except Exception as e : 
                    detail = f"Error while writting promo in db for --> {promo['promo_name']} --> "+str(e)
            else:
                status_code = 200
                detail= f"Promo already in db for --> {promo['promo_name']}"
        except Exception as e :
            detail= f"Error while getting promo from db for --> {promo['promo_name']} --> "+str(e)
    except Exception as e : 
        detail = "Error while convert pydantic to dict --> "+str(e)

    try :
        error.write_in_file(detail)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    raise HTTPException(status_code,detail)


