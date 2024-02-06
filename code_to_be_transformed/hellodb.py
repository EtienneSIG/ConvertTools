from sqlalchemy import create_engine,text
import pandas as pd
import tkinter
from tkinter import *
from tkinter import ttk

user_mysql = ""
password_mysql = ""
host_mysql = ""
db_mysql="testdb"
#user_postgres = ""
#password_postgres = ""
#host_postgres = ""
#db_postgres=""

window_main = tkinter.Tk(className='Hello from '+user_mysql, )
window_main.geometry("800x200")


ca_path="DigiCertGlobalRootCA.crt.pem"

cnx = create_engine(
    "mysql+pymysql://"+user_mysql+":"+password_mysql+"@"+host_mysql+"/"+db_mysql,
    connect_args={"ssl": {"ssl_ca": ca_path}},
)


def execute(engine,query) : 
    #query = "Select id, description, CURDATE() , ENCRYPT(description) from hello"
    
    #query ="ALTER TABLE hello AUTO_INCREMENT = 100"
    df = pd.read_sql(query, engine)
    return df

def getFunction(cnx,infoQuery) :
    info=execute(cnx,infoQuery)
    lbl.config(text="\n"+str(info))
    print(info)

################################################################
##Main Function
################################################################
if __name__ == "__main__":
    querySelectpart0= "ENCRYPT(description)"
    querySelectpart1 = "select id, description, CURDATE()," + querySelectpart0
    querySelectpart2 = "from hello"
    querySelect = querySelectpart1 + querySelectpart2
    #querySelect= "select id, description, CURDATE(), ENCRYPT(description) from hello"
    queryDatabase="Show Databases"
    queryInfos="SELECT VERSION()"


    button_submit = tkinter.Button(window_main, text ="Execute " + querySelect , command=lambda:getFunction(cnx,querySelect))
    button_submit.config(width=200, height=2)
    button_submit.pack()

    button_info = tkinter.Button(window_main, text ="get database", command=lambda:getFunction(cnx,queryDatabase))
    button_info.config(width=20, height=2)
    button_info.pack()

    button_info = tkinter.Button(window_main, text ="get Version", command=lambda:getFunction(cnx,queryInfos))
    button_info.config(width=20, height=2)
    button_info.pack()

    lbl = Label(window_main)
    lbl.pack()

    window_main.mainloop()
