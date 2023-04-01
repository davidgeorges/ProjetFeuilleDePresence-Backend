from fastapi import APIRouter, Body, Request,status
from fastapi.responses import JSONResponse
from config.hashPassword import verify_password
from classes.Database import database
from classes.Error import error as errorLogger
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

    db = database.get_db()

    try:

        user = jsonable_encoder(user_receive)
        user_from_db = await db["users"].find_one({"email": user["email"]})
        
        if user_from_db is None:
            return JSONResponse(content="User doesn't exist, please contact an admin.",status_code=status.HTTP_400_BAD_REQUEST)

        if not verify_password(user["password"],user_from_db["hashed_password"]) :
            return JSONResponse(content="Wrong credentials.",status_code=status.HTTP_401_UNAUTHORIZED)
            
        user_role = userRoleAsString(user_from_db["role_id"])
        if user_role is None : 
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = "Bearer "+token.create_token(user_from_db["_id"],user_role,"access")
        refresh_token = token.create_token(user_from_db["_id"],user_role,"refresh")
        await db["users"].update_one({"_id":user_from_db["_id"]},{"$set":{"refresh_token":refresh_token}})
        refresh_token = "Bearer "+refresh_token
        response = JSONResponse({"message" :"User connected with success.","id":user_from_db["_id"], "role" : user_role},status_code=status.HTTP_200_OK)
        response.set_cookie(key="access_token",value=access_token,httponly=True)
        response.set_cookie(key="refresh_token",value=refresh_token,httponly=True)
        return response
    
    except Exception as error : 
        errorLogger.write_in_file("login : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth.post("/logout")
async def logout():
    return JSONResponse("User disconnected with success.", status.HTTP_200_OK).delete_cookie("access_token").delete_cookie("refresh_token")

    

@auth.get("/authStatus")
async def auth_status(request : Request):

    db = database.get_db()

    try : 

        #Get the refresh_token from cookies
        refresh_token = request.cookies["refresh_token"]

        #If we have an user with the refresh_token
        user_from_db = await db["users"].find_one({"refresh_token":refresh_token.replace("Bearer ","")},{"email", "role_id"})

        #If user don't exist
        if user_from_db is None:
            return JSONResponse(content="Error no user with this refresh_token in the database.",status_code=status.HTTP_400_BAD_REQUEST)

        #Get the user role as a string
        user_role = userRoleAsString(user_from_db["role_id"])
        if user_role is None : 
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Check if is not expired
        if(token.check_if_is_expired(refresh_token, "refresh") != "OK"):
            return JSONResponse(content="Error refresh_token expired.",status_code=status.HTTP_401_UNAUTHORIZED)

        return JSONResponse(content={"message" :"User already connected.","id":user_from_db["_id"], "role" : user_role},status_code=status.HTTP_200_OK)

    except Exception as error :
        errorLogger.write_in_file("authStatus : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth.get("/refreshToken")
async def refresh_token(request : Request):

    db = database.get_db()

    try : 

        #Get the refresh_token from cookies
        refresh_token = request.cookies["refresh_token"]

        #Get user from the db
        user_from_db = await db["users"].find_one({"refresh_token" : refresh_token.replace("Bearer ", "")},{"email", "role_id"})

        #If user don't exist
        if user_from_db is None:
            return JSONResponse(content="Error no user with this refresh_token in the database.",status_code=status.HTTP_400_BAD_REQUEST)

        #Check if the refresh token is valid
        if(token.check_if_is_expired(refresh_token, "refresh") != "OK"):
            return JSONResponse(content="Error refresh_token expired.",status_code=status.HTTP_401_UNAUTHORIZED)
                    
        #Get the user role as a string
        user_role = userRoleAsString(user_from_db["role_id"])
        if user_role is None : 
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Create the access token
        access_token = "Bearer " +token.create_token(user_from_db["_id"], user_role, "access")
        response = JSONResponse(content={"message": "Refresh token success.", "id":user_from_db["_id"],"role": user_role},status_code=status.HTTP_200_OK)
        response.set_cookie(key="access_token",value=access_token,httponly=True)
            
        return response

    except Exception as error :
        errorLogger.write_in_file("refreshToken : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


