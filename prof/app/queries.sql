#database design for Prof2Student

studentId, firstName, lastName, school, graduationYear, major, email
professorId, firstName, lastName, school, department, email
courseId, professorId, courseName, semester, subject, description
courseId, timeOfAnnouncement, announcementContent
courseId, timeOfTopic, title, topicContent 
studentId, courseId

create database prof2student;

create table student(studentId serial, firstName char(50), lastName char(50), school char(100), graduationYear date, major char(100), email char(100));
create table professor(professorId serial, firstName char(50), lastName char(50), school char(100), department char(100), email char(100));
create table course(courseId serial, professorEmail char(100), courseName char(300), courseIdInCatalog char(20), semester char(20), description text);
create table announcement(announcementId serial, courseId int, timeOfAnnouncement time default current_timestamp, announcementContent text);
create table topic(topicId serial, courseId int, timeOfTopic time default current_timestamp, title char(300), topicContent text);
create table studentInCourse(studentFullName char(100), courseId int);



insert into student(firstName, lastName, school, graduationYear, major, email) values ();
update student SET school='', graduationYear='', major='', email='' where studentId='';

insert into professor(firstName, lastName, school, department, email) values();
update professor SET school='', department='', email='' where professorId='';

insert into course(professorId, courseName, semester, subject, description) values();
select * from course where professorId ='';
select * from course where semester = '';
select * from course where courseName = '';

insert into announcement(courseId, timeOfAnnouncement, announcementContent) values();
insert into topic(courseId, timeOfTopic, title, topicContent) values ();


insert into studentInCourse(studentId, courseId) values ();
select firstName, lastName from student, studentInCourse where courseId = '' and student.studentId = studentInCourse.studentId;
select content from course, studentInCourse where studentId = '' and course.courseId = studentInCourse.courseId;
