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

    #Init status code & content
    status_code = 500
    detail = "Internval error, please retry."
    errorMessage = ""

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
                        errorMessage = f"Error while inserting token in db for user with id : {user_from_db['_id']} --> {str(e)}"
                except Exception as e :
                    errorMessage = f"Error while creating token in db for user with id : {user_from_db['_id']} --> {str(e)}"
            else:   
                status_code = 401
                detail = "Wrong credentials."
                errorMessage = f"Error wrong credentials for user with id : {user_from_db['_id']}"
        else :
            status_code = 400
            detail = "User doesn't exist, please contact an admin."
            errorMessage = f"Error user trying to connect with non existing account, email used : {user_receive['email']}"
    except Exception as e : 
        errorMessage = f"Error while convert pydantic to dict --> {str(e)}"

    try :
        error.write_in_file(errorMessage)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

@auth.post("/logout")
async def logout():
    response = JSONResponse("User disconnected with success.",status.HTTP_200_OK)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@auth.get("/authStatus")
async def auth_status(request : Request):

    db = database.get_db()

    #Init status code & content
    status_code = 401
    detail = ""
    errorMessage = ""

    try : 
        #Get the refresh_token from cookies
        refresh_token = request.cookies["refresh_token"]
        try :
            #If we have an user with the refresh_token
            user_from_db = await db["users"].find_one({"refresh_token":refresh_token.replace("Bearer ","")},{"email", "role_id"})
            #Get the user role as a string
            user_role = userRoleAsString(user_from_db["role_id"])
            #Check if is not expired
            if(token.check_if_is_expired(refresh_token, "refresh") == "OK"):
                return JSONResponse(content={"message" :"User already connected.","id":user_from_db["_id"], "role" : user_role},status_code=status.HTTP_200_OK)
            else:
                detail = "Error refresh_token expired."
                errorMessage = "Error an user tried to reconnect with an expired refresh_token."
        except :
            detail = "Error no user with this refresh_token in the database."
            errorMessage = "Error an user tried to reconnect with an non existing refresh_token."
    except :
        detail =  "No access - Missing refresh_token."
        errorMessage =  "Error an user tried to reconnect without  refresh_token."


    try :
        error.write_in_file(errorMessage)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

@auth.get("/refreshToken")
async def refresh_token(request : Request):

    db = database.get_db()

    #Init status code & content
    status_code = 401
    detail = "Internval error, please retry."
    errorMessage = ""
    
    try : 
        #Get the refresh_token from cookies
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
                    detail = "Error refresh_token expired."
                    errorMessage = "Error an user tried to reconnect with an expired refresh_token."
            else:
                detail = "Error no user with this refresh_token in the database."
                errorMessage = "Error an user tried to reconnect with an non existing refresh_token."
        except Exception as e:
            status_code = 500
            errorMessage = f"Error while convert pydantic to dict --> {str(e)}"
    except :
        detail =  "No access - Missing refresh_token."
        errorMessage =  "No access - Missing refresh_token."

    try:
        error.write_in_file(errorMessage)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)

