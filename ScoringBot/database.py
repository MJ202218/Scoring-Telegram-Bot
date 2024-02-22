import mysql.connector
from tabulate import tabulate
def connection():
    try:
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234",
            database = "phase_2"
        )
        if db.is_connected():
            print("connected succesfully✅")
        mycursor = db.cursor()
        mycursor.execute("select userid, username, email from user")
        info = mycursor.fetchall()
        print(info)
        print(tabulate(info, tablefmt="fancy_grid", showindex=True))
    except Exception as e:
        print("Error while connecting to MySQL", e)

    finally:
        if db.is_connected():
            mycursor.close()
            db.close()
            print("MySQL connection is closed")


if __name__ == '__main__':
    connection()