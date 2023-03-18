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

    db = database.get_db()

    try:

        user = jsonable_encoder(user_receive)
        user_from_db = await db["users"].find_one({"email": user["email"]})

        if ( user_from_db ) is None:
            raise HTTPException(400, "User doesn't exist, please contact an admin.")

        if not verify_password(user["password"],user_from_db["hashed_password"]) :
            raise HTTPException(401, "Wrong credentials.")
            
        user_role = userRoleAsString(user_from_db["role_id"])
        access_token = "Bearer "+token.create_token(user_from_db["_id"],user_role,"access")
        refresh_token = token.create_token(user_from_db["_id"],user_role,"refresh")
        await db["users"].update_one({"_id":user_from_db["_id"]},{"$set":{"refresh_token":refresh_token}})
        refresh_token = "Bearer "+refresh_token
        response = JSONResponse(content={"message" :"User connected with success.","id":user_from_db["_id"], "role" : user_role},status.HTTP_200_OK)
        response.set_cookie(key="access_token",value=access_token,httponly=True)
        response.set_cookie(key="refresh_token",value=refresh_token,httponly=True)
        return response
     
    except Exception as error : 
        error.write_in_file(str(error))
        raise HTTPException(500)


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

        #Get the user role as a string
        user_role = userRoleAsString(user_from_db["role_id"])

        #Check if is not expired
        if(token.check_if_is_expired(refresh_token, "refresh") != "OK"):
            raise HTTPException(401,"Error refresh_token expired.")

        return JSONResponse(content={"message" :"User already connected.","id":user_from_db["_id"], "role" : user_role},status.HTTP_200_OK)

    except Exception as error :
        error.write_in_file(error)
        raise HTTPException(500)


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
            raise HTTPException(400,"Error no user with this refresh_token in the database.")

        #Check if the refresh token is valid
        if(token.check_if_is_expired(refresh_token, "refresh") != "OK"):
            raise HTTPException(401,"Error refresh_token expired.")
                    
        #Get the user role as a string
        user_role = userRoleAsString(user_from_db["role_id"])

        #Create the access token
        access_token = "Bearer " +token.create_token(user_from_db["_id"], user_role, "access")
        response = JSONResponse(content={"message": "Refresh token success.", "id":user_from_db["_id"],"role": user_role},status.HTTP_200_OK)
        response.set_cookie(key="access_token",value=access_token,httponly=True)
            
        return response

    except Exception as error :
        error.write_in_file(error)
        raise HTTPException(500)


