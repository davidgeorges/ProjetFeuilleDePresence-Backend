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
async def set_student_status(dailyToken: str, request: Request):

    db = database.get_db()
    access_token = request.cookies.get("access_token")

    student_id = token.get_data("id", access_token, "access")
    if not student_id:
    return JSONResponse("Invalid access token", status.HTTP_401_UNAUTHORIZED)

    student = await db["users"].find_one({"_id": student_id}, {"promo_id", "status"})
    if not student:
    return JSONResponse("Student not found", status.HTTP_404_NOT_FOUND)

    today = datetime.today().strftime("%d-%m")
    if today in student["status"]:
    return JSONResponse("You have already declared your presence.", status.HTTP_400_BAD_REQUEST)

    promo = await db["promo"].find_one({"_id": student["promo_id"]}, {"daily_token"})
    if not promo:
    return JSONResponse("Promo not found", status.HTTP_404_NOT_FOUND)

    if promo["daily_token"] != dailyToken:
    return JSONResponse("Invalid daily token", status.HTTP_400_BAD_REQUEST)

    status_updated = {today: "present", **student["status"]}
    await db["users"].update_one({"_id": student_id}, {"$set": {"status": status_updated}})
    return JSONResponse("Success", status.HTTP_201_CREATED)