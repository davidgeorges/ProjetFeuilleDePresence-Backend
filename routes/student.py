from fastapi import APIRouter, Request,status
from fastapi.responses import JSONResponse
from classes.Database import database
from classes.Error import error as errorLogger
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
async def set_student_status(dailyToken: str, request: Request):

    db = database.get_db()

    if datetime.now().weekday() == 5 or datetime.now().weekday() == 6 :
        return JSONResponse(content="You cannot set your status on weekends.",status_code=status.HTTP_400_BAD_REQUEST)

    access_token = request.cookies.get("access_token")
    try:
        student_id = token.get_data("id", access_token, "access")
        if not student_id:
            return JSONResponse(content="Invalid access token",status_code=status.HTTP_401_UNAUTHORIZED)

        student = await db["users"].find_one({"_id": student_id}, {"promo_id", "status"})
        if not student:
            return JSONResponse(content="Student not found",status_code=status.HTTP_404_NOT_FOUND)

        today = datetime.today().strftime("%d-%m")
        if today in student["status"]:
            return JSONResponse(content="You have already declared your presence.",status_code=status.HTTP_400_BAD_REQUEST)

        promo = await db["promo"].find_one({"_id": student["promo_id"]}, {"daily_token"})
        if not promo:
            return JSONResponse(content="Promo not found",status_code=status.HTTP_404_NOT_FOUND)

        if promo["daily_token"] != dailyToken:
            return JSONResponse(content="Invalid daily token",status_code=status.HTTP_400_BAD_REQUEST)

        status_updated = {today: "present", **student["status"]}
        await db["users"].update_one({"_id": student_id}, {"$set": {"status": status_updated}})

        return JSONResponse(content="Success",status_code=status.HTTP_201_CREATED)
    except Exception as error :
        errorLogger.write_in_file("setMyStatus : "+str(error))
        return JSONResponse(content="",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)