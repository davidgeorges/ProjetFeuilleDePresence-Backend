from datetime import date,datetime

"""
Error file.
@Author : David GEORGES
"""

class Error : 

    #private members
    __file_name  = " "
    __file = None

    def __init__(self):
        try : 
            self.set_file_name()
        except Exception as e : 
            print("Error while setting file name --> ",e)

    def set_file_name(self):
        self.__file_name = "Error-Log-"+str(date.today().strftime("%d-%m-%Y"))+'.txt'

    def open_file(self):
        self.__file = open("./error/"+self.__file_name,"a")

    def write_in_file(self,error_receive):
        self.open_file()
        self.__file.write(datetime.now().strftime("%H:%M")+" : "+error_receive+"\n")
        self.__file.close()
        print("New error in log file.")

error = Error()
