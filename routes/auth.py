from fastapi import APIRouter, Body, Request,status
from fastapi.responses import JSONResponse
from config.hashPassword import verify_password
from classes.Database import database
from classes.Error import error
from classes.Token import token
from fastapi.encoders import jsonable_encoder
from models.user import UserIn

"""
File containing auth route.
@Author : David GEORGES
"""

auth = APIRouter()


#Return user role as string (Switch Case using Dictionary Mapping)
def userRoleAsString(value):
    switcher = {
        "1" : "student",
        "2" : "teacher",
        "3" : "admin",
    }
    return switcher.get(value)

#Login user
@auth.post("/login")
async def login(user_receive: UserIn = Body(...)):

    print(user_receive)

    db = database.get_db()

    #Init status code & content
    status_code = 500
    detail = { "message" : "" }

    try :
        #Convert pydantic model to a Dict
        user = jsonable_encoder(user_receive)
        #Get the user from database
        user_from_db = await db["users"].find_one({"email": user["email"]})
        #If user exist
        if ( user_from_db ) is not None:
            #Check password from user and database
            if verify_password(user["password"],user_from_db["hashed_password"]) :
                try :   
                    #Get the user role as a string
                    user_role = userRoleAsString(user_from_db["role_id"])
                    #Create token and refresh token with user id and role
                    access_token = "Bearer "+token.create_token(user_from_db["_id"],user_role,"access")
                    refresh_token = token.create_token(user_from_db["_id"],user_role,"refresh")
                    try :
                        #Insert refresh_token in db
                        await db["users"].update_one({"_id":user_from_db["_id"]},{"$set":{"refresh_token":refresh_token}})
                        refresh_token = "Bearer "+refresh_token
                        response = JSONResponse(content={"message" :"User connected with success.","id":user_from_db["_id"], "role" : user_role},status_code=status.HTTP_200_OK)
                        response.set_cookie(key="access_token",value=access_token,httponly=True)
                        response.set_cookie(key="refresh_token",value=refresh_token,httponly=True)
                        return response
                    except Exception as e :
                        detail["message"] = "Error while inserting token in db --> "+str(e)
                except Exception as e :
                    detail["message"] = "Error while creating token --> "+str(e)
            else:   
                status_code = 401
                detail["message"] = "Wrong credentials."
        else :
            status_code = 400
            detail["message"] = "User doesn't exist, please contact an admin."
    except Exception as e : 
        detail["message"] =  "Error while convert pydantic to dict --> "+str(e)

    try :
        error.write_in_file(detail["message"])
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

@auth.post("/logout")
async def logout():
    response = JSONResponse(content={"message" :"User disconnected with success."},status_code=status.HTTP_200_OK)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@auth.post("/authStatus")
async def auth_status(request : Request):

    #Init status code & content
    status_code = 500
    detail = { "message" : "" }

    #Get the refresh_token from cookies
    refresh_token = request.cookies["refresh_token"]
    
    #Check if is not expired
    if(token.check_if_is_expired(refresh_token, "refresh") == "OK"):
        print(request)
    else:
        detail["message"] = "Error refresh_token expired."

    try :
        error.write_in_file(detail["message"])
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

@auth.get("/refreshToken")
async def refresh_token(request : Request):

    db = database.get_db()
    #Init status code & content
    status_code = 500
    detail = { "message" : "" }
    
  
    refresh_token = request.cookies["refresh_token"]
    try : 
        #Get user from the db
        user_from_db = await db["users"].find_one({"refresh_token" : refresh_token.replace("Bearer ", "")},{"email", "role_id"})
        #If user exist
        if user_from_db is not None:
            #Check if the refresh token is valid
            if(token.check_if_is_expired(refresh_token, "refresh") == "OK"):
                #Get the user role as a string
                user_role = userRoleAsString(user_from_db["role_id"])
                #Create the access token
                access_token = "Bearer " +token.create_token(user_from_db["_id"], user_role, "access")
                response = JSONResponse(content={"message": "Refresh token success.", "id":user_from_db["_id"],"role": user_role},status_code=status.HTTP_200_OK)
                response.set_cookie(key="access_token",value=access_token,httponly=True)
                return response
            else:
                #Invalid refresh token
                status_code = 401
                detail["message"] = "Error - " + token.get_token_error()
        else:
            status_code = 401
            detail["message"] = "Error - No user with this refresh token"
    except Exception as e:
        detail["message"] = " Error while convert pydantic to dict --> "+str(e)

    try:
        error.write_in_file(detail["message"])
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

