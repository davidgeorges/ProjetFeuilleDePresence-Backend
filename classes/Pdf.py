from fpdf import FPDF

"""
Pdf file.
@Author : David GEORGES
"""

class Pdf(FPDF):

    __title = ""
    __date = ""
    __file_name = ""

    def header(self):
        self.image("./images/CY-Cergy-Paris-logo.png", 15, 12.5, 40, 15)
        self.set_font("helvetica", 'B', 16)
        self.cell(0, 20, self.title, 0, align="C")
        self.ln(30)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", 'I', 8)
        self.cell(0, 5, self.date + " - CY CERGY PARIS - N°"+str(self.page_no()), 0, align="C")

    def createPdf(self,dataReceive) :

        TABLE_COL_NAMES = ("Nom", "Prenom", "Mail", "Status")

        self.add_page()
        line_height = self.font_size * 1.7
        col_width = self.epw / 4
        self.set_font_size(12)

        #Adding column names from array
        for col_name in TABLE_COL_NAMES:
                self.cell(col_width, line_height, col_name, border=1,align="C")
        self.ln(line_height)

        #Line break
        self.ln(5)
        self.set_font_size(10)
        #Adding value from array
        for row in dataReceive:
            for datum in row:
                self.multi_cell(col_width, line_height, datum, border=1,
                        new_x="RIGHT", new_y="TOP", max_line_height=self.font_size)
            self.ln(line_height)

        #
        self.__file_name = self.title+'-'+self.date+'.pdf'
        self.output("./pdf/"+self.__file_name)

    def setTitle(self,titleReceive) :
        self.title = titleReceive

    def setDate(self,dateReceive) :
        self.date = dateReceive
    
    def getFileName(self) :
        return self.__file_name
