from fastapi import FastAPI,Request,status
from routes.teacher import teacher
from routes.student import student
from routes.admin import admin
from routes.auth import auth
from classes.Token import token
from fastapi.responses import JSONResponse
from classes.Error import error as errorLogger
from fastapi.middleware.cors import CORSMiddleware

"""
@Author : David GEORGES
"""

app = FastAPI()


@app.middleware("http")
async def token_filter(request: Request,call_next):

    #Get the url path as an array
    request_splited = request.url.path.split("/")

    #No rights needed for AUTH path
    if "auth" in request_splited :
        return await call_next(request)
    
    try :
        
        #Get the refresh_token from cookies
        refresh_token = request.cookies["refresh_token"]
        #Check if is expired
        if(token.check_if_is_expired(refresh_token, "refresh") != "OK"):
            return JSONResponse(content="Error refresh_token expired.",status_code=status.HTTP_401_UNAUTHORIZED)

        #Get the access_token from cookies
        access_token = request.cookies["access_token"]
        #Check if is expired
        if(token.check_if_is_expired(access_token, "access") != "OK"):
            return JSONResponse(content="Error access_token expired.",status_code=status.HTTP_401_UNAUTHORIZED)

        #Get the user role
        user_role = token.get_data("role",access_token,"access")
        #If we have no role from token
        if user_role is None : 
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Check if the user his not an admin and if he doesn't have the role to access the resource
        if user_role not in request_splited and user_role != "admin":
            return JSONResponse(content="No access - Missing rights.",status_code=status.HTTP_403_FORBIDDEN)

        return await call_next(request)

    except Exception as error :                   
        errorLogger.write_in_file(" middleware : "+str(error))
        return JSONResponse(content="",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



origins = [
    "http://localhost:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth,prefix="/api/auth")   
app.include_router(teacher,prefix="/api/teacher")
app.include_router(student,prefix="/api/student")
app.include_router(admin,prefix="/api/admin")

