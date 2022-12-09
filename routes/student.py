from fastapi import APIRouter
from fastapi.responses import JSONResponse

"""
File containing student routes.
@Author : David GEORGES
"""

student = APIRouter()

@student.get('/setMyStatus/{token}',)
async def set_student_status():
    return {"Request : my student !"}