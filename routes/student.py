from fastapi import APIRouter, Request,status
from fastapi.responses import JSONResponse
from classes.Database import database
from classes.Error import error
from classes.Token import token
from datetime import datetime

"""
File containing student routes.
@Author : David GEORGES
"""

student = APIRouter()


#Note 12-12
"""
To add  :
    Vérifiez si ce n'est pas férié ou les vacances...
"""
@student.get('/setMyStatus/{dailyToken}')
async def set_student_status(dailyToken : str,request: Request):


    db = database.get_db()
    
    #Init status code & content
    status_code = 500
    detail = "Internval error, please retry."
    errorMessage = ""
    
    # Check if it's a weekday
    if datetime.today().weekday() < 5:  
        #Get the access_token from cookies
        access_token = request.cookies["access_token"]
        
        #Get the user id
        student_id = token.get_data("id",access_token,"access")

        #If we have any id from token
        if student_id is not None : 
            try : 
                #Get the student from is id
                student_from_db = await db["users"].find_one({"_id" : student_id},{"promo_id","status"})
                todayDateAndMonth = datetime.today().strftime("%d-%m")
                #Check if the user has not already justified his presence
                if todayDateAndMonth not in student_from_db["status"].keys() : 
                    try : 
                        #Get the promo linked to the student
                        promo_from_db = await db["promo"].find_one({"_id": student_from_db["promo_id"]},{"daily_token"})
                        #If the promo exist
                        if promo_from_db is not None : 
                            #Check if the daily_token of the user entry is the same as the one in the database
                            if promo_from_db["daily_token"] == dailyToken :
                                try : 
                                    #Concat dict
                                    statusUpdated = dict({todayDateAndMonth:"present"},**student_from_db["status"])
                                    try : 
                                        #Update in database
                                        await db["users"].update_one({"_id":student_id},{"$set":{"status":statusUpdated}})
                                        return JSONResponse("Success",status.HTTP_201_CREATED)
                                    except Exception as e : 
                                        detail = "Error, please try later."
                                        errorMessage = f"Error while updating status for user with id : {student_id} and promo id : {student_from_db['promo_id']}"
                                except Exception as e :
                                    errorMessage = f"Error while concatenating dict for user with id : {student_id} and promo id : {student_from_db['promo_id']} --> {str(e)}"
                            else : 
                                detail = "Unvalid token, please retry."
                                return JSONResponse(detail,status.HTTP_202_ACCEPTED)
                        else :
                            detail = "You are linked to a non-existent promotion, please contact an admin."
                            errorMessage = f"Error non-existent promo for user with id : {student_id} and promo id : {student_from_db['promo_id']}"
                    except Exception as e :
                        errorMessage = f"Error while getting promo with id : {student_from_db['promo_id']} for user with id {student_id}"
                else :
                    detail = "You have already declared your presence."
                    return JSONResponse(detail,status.HTTP_202_ACCEPTED)
            except Exception as e :
                errorMessage = f"Error while getting student with id  :  {student_id}"
        else :
            errorMessage = f"Error while decoding no id in the token : {access_token}"  
    else:  
        detail = "You cannot declare your presence on weekends."
        return JSONResponse(detail,status.HTTP_202_ACCEPTED)

    
    try :
        error.write_in_file(errorMessage)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)