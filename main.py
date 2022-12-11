from fastapi import FastAPI,Request
from routes.teacher import teacher
from routes.student import student
from routes.admin import admin
from routes.auth import auth
from classes.Token import token
from fastapi.responses import JSONResponse
from classes.Error import error
from fastapi.middleware.cors import CORSMiddleware

"""
@Author : David GEORGES
"""

app = FastAPI()


@app.middleware("http")
async def token_filter(request: Request,call_next):

    #Init status code & content
    status_code = 401
    errorMessage = ""
    
    #Get the url path as an array
    request_splited = request.url.path.split("/")

    #No rights needed for AUTH path
    if "auth" in request_splited :
        return await call_next(request)
    
    try :
        #Get the refresh_token from cookies
        refresh_token = request.cookies["refresh_token"]
        #Check if is not expired
        if(token.check_if_is_expired(refresh_token, "refresh") == "OK"):
            try :
                #Get the access_token from cookies
                access_token = request.cookies["access_token"]
                #Check if is not expired
                if(token.check_if_is_expired(access_token, "access") == "OK"):
                    #Get the user role
                    user_role = token.get_data("role",access_token,"access")
                    #If we have any role from token
                    if user_role is not None : 
                        #Admin can access all routes
                        #Check if the user has the role to access the resource
                        if user_role in  request_splited or user_role == "admin" :
                            try :
                                #Access to the initial request
                                return await call_next(request)
                            except Exception as e:
                                status_code = 500
                                errorMessage =  "Error with the route."
                        else :
                            status_code = 403
                            errorMessage = "No access - Missing rights."
                    else:
                        status_code = 500
                        errorMessage =  "Error while getting user role."
                else:
                    errorMessage = "Error access_token expired."
            except :
                errorMessage =  "No access - Missing access_token."
        else:
            errorMessage = "Error refresh_token expired."
    except :
        errorMessage =  "No access - Missing refresh_token."
        

    try :
        error.write_in_file(errorMessage)
    except Exception as e : 
        print("Error while trying to write in file --> "+str(e))
    return JSONResponse(errorMessage, status_code)



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

