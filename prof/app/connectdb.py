import psycopg2

def connect():
    return psycopg2.connect("dbname='' user='' host='' password='' port=''")

##specify function to connect to database

def insertProfessor(given_name, family_name, email):
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into professor(firstName, lastName, email) values (%s, %s, %s)",
		(given_name, family_name, email))
    conn.commit()
    cur.close()
    conn.close()    

def insertStudent(given_name, family_name, email):
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into student(firstName, lastName, email) values (%s, %s, %s)",
		(given_name, family_name, email))
    conn.commit()
    cur.close()
    conn.close()    

def addCourse(profEmail, name, courseId, semester, description):
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into course(professorEmail, courseName, courseIdInCatalog, semester, description) values (%s, %s, %s, %s, %s)",
		(profEmail, name, courseId, semester, description))
    conn.commit()
    cur.close()
    conn.close()

def viewAllCourse(profEmail):
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from course where professorEmail = %s",
		(profEmail,))
    rows = []
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def getDescription(courseId):
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from course where courseId = %s",
		(courseId,))
    row = []
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[2], row[5]

def addTopic(courseId, title, text):
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into topic(courseId, title, topicContent) values (%s, %s, %s)",
		(str(courseId), title, text))
    conn.commit()
    cur.close()
    conn.close()

def viewAllTopic(courseId):
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from topic where courseId = %s",
		(courseId,))
    rows = []
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def addAnnouncement(courseId, text):
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into announcement(courseId, announcementContent) values (%s, %s)",
		(str(courseId), text))
    conn.commit()
    cur.close()
    conn.close()

def viewAllAnnouncement(courseId):
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from announcement where courseId = %s order by timeOfAnnouncement desc",
		(courseId,))
    rows = []
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def viewAllStudent(courseId):
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from studentInCourse where courseId = %s order by studentFullName",
		(courseId,))
    rows = []
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows    

#insertProfessor("abc", "xyz", "123")
