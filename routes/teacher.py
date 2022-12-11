from fastapi import APIRouter, Request,status
from fastapi.responses import JSONResponse
from classes.Database import database
from classes.Error import error
from classes.Token import token

"""
File containing teacher routes.
@Author : David GEORGES
"""

teacher = APIRouter()

#Will return an array containing all data of users of the promo
async def get_all_student_data(student_list):

    db = database.get_db()
    all_student_data = []

    for student_id in student_list :
        try :
            student_data = await db["users"].find_one({"_id" : student_id},{"email","last_name","first_name","status"})
            all_student_data.append(student_data)
        except Exception as e : 
            try :
                error.write_in_file(f"Error while getting student data from db --> {student_id} --> "+str(e))
            except Exception as e : 
                print("Error while trying to write in file --> "+str(e))
                
    return all_student_data

#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/getMyPromo")
async def get_all_data_from_promo(request: Request):

    db = database.get_db()

    #Init status code & content
    status_code = 500
    detail = " "

    #Get the access_token from cookies
    access_token = request.cookies["access_token"]
    
    #Get the user id
    teacher_id = token.get_data("id",access_token,"access")

    #If we have any id from token
    if teacher_id is not None : 
        try : 
            #Get the teacher from is id
            teacher_from_db = await db["users"].find_one({"_id" : teacher_id},{"promo_id"})
            try : 
                #Get the promo linked to the teacher
                promo_from_db = await db["promo"].find_one({"_id": teacher_from_db["promo_id"]})
                #If promo the exist
                if promo_from_db is not None : 
                    try :
                        #Get all student data in an array
                        all_student_data = await get_all_student_data(promo_from_db["student_list"])
                        #If we have at least one student
                        if all_student_data :
                            response_data = {"payload_student_list" : all_student_data}
                            #Check if the teacher is the one who has to teach this day, if so we can send the payload_daily_token
                            if teacher_id == promo_from_db["daily_teacher_id"] : 
                                response_data["payload_daily_token"] = promo_from_db["daily_token"]
                            return JSONResponse(response_data, status.HTTP_200_OK)
                        else : 
                            return JSONResponse("No user in this promo.", status.HTTP_204_NO_CONTENT)
                    except Exception as e :
                        detail =  f"Error while getting all student data from db - student_list --> {promo_from_db['student_list']} --> "+str(e)
                else :
                    status_code = 400
                    detail = f"Promo not in db for --> {promo_from_db['promo_name']} - for --> {teacher_id}"
            except Exception as e :
                detail = f"Error while getting promo from db - promo_id --> {teacher_from_db['promo_id']} --> "+str(e)
        except Exception as e :
            detail =  f"Error while getting teacher from db - teacher_id --> {teacher_id} --> "+str(e)
    else : 
        detail =  "No access - teacher_id is none."

    try :
        error.write_in_file(detail["message"])
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)


#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/downloadWeeklySummary")
async def download_weekly_summary(request: Request):

    db = database.get_db()

    #Init status code & content
    status_code = 500
    detail = " "


    try :
        error.write_in_file(detail["message"])
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(detail, status_code)