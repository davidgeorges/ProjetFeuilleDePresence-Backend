from datetime import datetime,date, timedelta
from fastapi import APIRouter, Request,status
from fastapi.responses import JSONResponse
from classes.Pdf import Pdf
from classes.Database import database
from classes.Error import error as errorLogger
from classes.Token import token
from fastapi.responses import FileResponse

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
            errorLogger.write_in_file(f"Error while getting student data from db --> {student_id} --> "+str(e))
    return all_student_data

#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/getMyPromo")
async def get_all_data_from_promo(request: Request):

    db = database.get_db()
    access_token = request.cookies["access_token"]
    teacher_id = token.get_data("id",access_token,"access")

    #If we have no id from token
    if teacher_id is None : 
        return JSONResponse(status.HTTP_500_INTERNAL_SERVER_ERROR)
    try : 
        #Get the teacher from is id
        teacher = await db["users"].find_one({"_id" : teacher_id},{"promo_id"})
        promo = await db["promo"].find_one({"_id": teacher["promo_id"]})
        #If promo don't exist
        if promo is None : 
            return JSONResponse(content=f"Promo not in db for --> {promo['promo_name']} - for --> {teacher_id}",status_code=status.HTTP_400_BAD_REQUEST) 
        #Get all student data in an array
        all_student_data = await get_all_student_data(promo["student_list"])
        #If we have no student
        if not all_student_data :
            return JSONResponse(content="No user in this promo.",status_code=status.HTTP_400_BAD_REQUEST)

        response = {"payload_student_list": all_student_data}
        if teacher_id == promo["daily_teacher_id"]:
            response["payload_daily_token"] = promo["daily_token"]

        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    except Exception as error :
            errorLogger.write_in_file("getMyPromo : "+str(error))
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/download/summary/{date}")
async def download_weekly_summary(date : str,request: Request):

    db = database.get_db()
    access_token = request.cookies["access_token"]
    teacher_id = token.get_data("id",access_token,"access")
    student_list = list()

    #If we have no id from token
    if teacher_id is None :
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try :
        #Get teacher promo id
        teacher = await db["users"].find_one({"_id" : teacher_id},{"promo_id"})
        #Get the promo
        promo = await db["promo"].find_one({"_id" : teacher["promo_id"]},{"promo_id","promo_name","promo_year"})
        #Get all user of the promo with the status of the day
        async for value in db["users"].find({"promo_id" : teacher["promo_id"],"role_id" : "1"},{"last_name","first_name",f"status.{date}","email"}):
            student_status = value["status"][date] if value["status"] else "absent"
            student_list.append((value["last_name"],value["first_name"],value["email"],student_status))
        #Convert list to tupple
        student_tuple = tuple(student_list)
        #Pdf set title,date and create pdf
        pdf = Pdf()
        pdf.setTitle(promo["promo_name"].upper()+"-"+promo["promo_year"].upper())
        pdf.setDate(date)
        pdf.createPdf(student_tuple)
        return FileResponse(path="./pdf/"+pdf.getFileName(),status_code=status.HTTP_200_OK,media_type='application/pdf')
    except Exception as error :
        errorLogger.write_in_file("downloadSummary : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/getAllPromo/{date}")
async def get_all_promo(date : str,request: Request):

    db = database.get_db()
    access_token = request.cookies["access_token"]
    teacher_id = token.get_data("id",access_token,"access")

    if datetime.now().weekday() == 5 | datetime.now().weekday() == 6 :
        return JSONResponse(content="You cannot get promo on weekends.",status_code=status.HTTP_400_BAD_REQUEST)

    #If we have no id from token
    if teacher_id is None : 
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try : 
        #Get teacher promo id
        teacher = await db["users"].find_one({"_id" : teacher_id},{"promo_id"})
        #Get all user of the promo with the status of the day
        status_list = []
        async for x in db["users"].find({"promo_id" : teacher["promo_id"],"role_id" : "1"},{f"status.{date}","email","last_name","first_name"}):
            status_list.append(x)
        return JSONResponse(content=status_list,status_code=status.HTTP_200_OK)
    except Exception as error :
        errorLogger.write_in_file("getAllPromo : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Respond with an array containg all data of users of the promo AND an daily token if the teacher have access
@teacher.get("/getWeekday")
async def get_weekday():

    list_of_weekday = []
    detail = ""
    if datetime.now().weekday() != 5 | datetime.now().weekday() != 6 :
        for i in range(datetime.now().weekday()+1) :
            list_of_weekday.append(date_for_weekday(i).strftime("%d-%m"))
    else : 
        detail = "You cannot access this view on weekends."
    return JSONResponse(content={"payload" : list_of_weekday,"message" : detail},status_code=status.HTTP_200_OK)

@teacher.get("/getPromoName")
async def get_weekday(request: Request):

    db = database.get_db()
    access_token = request.cookies["access_token"]
    teacher_id = token.get_data("id",access_token,"access")

    #If we have any id from token
    if teacher_id is None : 
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try : 
        #Get the teacher from is id
        teacher = await db["users"].find_one({"_id" : teacher_id},{"promo_id"})
        #Get the promo linked to the teacher
        promo = await db["promo"].find_one({"_id": teacher["promo_id"]},{"promo_name","promo_year"})
        return JSONResponse(content=promo["promo_name"].upper()+"-"+promo["promo_year"].upper(),status_code=status.HTTP_200_OK) 
    except Exception as error :
        errorLogger.write_in_file("getPromoName : "+str(error))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def date_for_weekday(day: int):
    today = date.today()
    # weekday returns the offsets 0-6
    # If you need 1-7, use isoweekday
    weekday = today.weekday()
    return today + timedelta(days=day - weekday)

