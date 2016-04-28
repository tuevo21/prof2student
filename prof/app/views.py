from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from app import app

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from connectdb import *

CLIENT_ID = json.loads(
    open('app/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Prof2Student"


@app.route('/')
@app.route('/index')
def index():
    return redirect('/login')

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

#create gconnect for login authentication
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('app/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['given_name'] = data['given_name']
    login_session['family_name'] = data['family_name']
    login_session['html_course'] = getProfessorHTMLCourse()

    insertProfessor(login_session['given_name'], login_session['family_name'], login_session['email'])

    output = ''
    output += '<p>Welcome, Professor '
    output += login_session['family_name']
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    if 'username' not in login_session:
        return redirect('/login')
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return redirect('/login')
    else:
	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

#for professors


def getProfessorHTMLCourse():
    courses = viewAllCourse(login_session['email'])
    html_course = ''
    for course in courses:
	html_course += '<li><a href=/professor/' + str(course[0]) + '/content><span class="glyphicon glyphicon-book"></span> ' + course[2] + '</a></li>';
    return html_course

def getProfessorLinks(course_id):
    return ''.join(['<li><a href="', '/professor/' , str(course_id), '/announcement', '">Announcement</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/content', '">Course content</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/student','">Student</a></li>']) 


@app.route('/professor/addCourse', methods=['GET', 'POST'])
def showProfessorAddCourse():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        addCourse(login_session['email'], request.form['name'], request.form['id'], request.form['semester'], request.form['description'])
        flash('successfully add course')
        login_session['html_course'] = getProfessorHTMLCourse() #update course list
	return render_template('profAddCourse.html', submit_status = 'Success!', current_courses = login_session['html_course'])
    else:
        login_session['html_course'] = getProfessorHTMLCourse() #update course list
    	return render_template('profAddCourse.html', current_courses = login_session['html_course'])



@app.route('/professor/<int:course_id>/content/', methods=['GET', 'POST'])
def showProfessorContent(course_id):
    if 'username' not in login_session:
        return redirect('/login')
    #get course name and description from db
    name_and_description = getDescription(course_id)
    name = name_and_description[0]
    description = name_and_description[1]
    #get list of topics from db
    topics = viewAllTopic(course_id)
    html_topic = ''
    i = 0
    for topic in topics:
	if (i %2 == 0):    	
		curr = '<div class="row"><div class="col-lg-6"><div class="panel panel-default"><div class="panel-heading"><strong>Topic: '
		curr +=	topic[3]
		curr += '</strong></div><div class="panel-body">'
		curr += topic[4] 
		curr += '</div></div></div>'	
		html_topic += curr
	else:
		curr = '<div class="col-lg-6"><div class="panel panel-default"><div class="panel-heading"><strong>Topic: '
		curr +=	topic[3]
		curr += '</strong></div><div class="panel-body">'
		curr += topic[4] 
		curr += '</div></div></div></div><br>'	
		html_topic += curr
	i+=1
    #accept new addition
    if request.method == 'POST':
	addTopic(course_id, request.form['title'], request.form['text'])
	flash('successfully add topic')
    	return redirect('/professor/' + str(course_id) + '/content/')

    #create reference link for top bar
    html_link = ''.join(['<li><a href="', '/professor/' , str(course_id), '/announcement', '">Announcement</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/content', '">Course content</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/student','">Student</a></li>']) 

    return render_template('profContent.html', current_courses = login_session['html_course'], course_name=name, 
		course_description=description, topics = html_topic, links = getProfessorLinks(course_id))



@app.route('/professor/<int:course_id>/announcement/', methods=['GET', 'POST'])
def showProfessorAnnouncement(course_id):
    if 'username' not in login_session:
        return redirect('/login')    
    announcements = viewAllAnnouncement(course_id)
    html_announcement = ''
    for announcement in announcements:
	html_announcement += '<div class="row"><div class="col-lg-11"><div class="panel panel-info"><div class="panel-heading"><strong>' 
	html_announcement += 'Professor ' + login_session['family_name']
	html_announcement += '</strong></div><div class="panel-body">'
	html_announcement += announcement[3]
	html_announcement += '</div></div></div></div><br>'

    if request.method == 'POST':
	addAnnouncement(course_id, request.form['text'])	
	flash('successfully add anouncement')
	return redirect('/professor/' + str(course_id) + '/announcement/')
    #create reference link for top bar
    html_link = ''.join(['<li><a href="', '/professor/' , str(course_id), '/announcement', '">Announcement</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/content', '">Course content</a></li>', 
			'<li><a href="', '/professor/' , str(course_id), '/student','">Student</a></li>']) 
    return render_template('profAnnouncement.html', current_courses = login_session['html_course'], 
			announcements = html_announcement, links = getProfessorLinks(course_id))



@app.route('/professor/<int:course_id>/student/', methods=['GET', 'POST'])
def showProfessorStudent(course_id):
    if 'username' not in login_session:
        return redirect('/login')
    students = viewAllStudent(course_id)
    html_student = ''
    for student in students:
	html_student += '<li>'
	html_student += student[0]
	html_student += '</li>'
    
    return render_template('profStudent.html', current_courses = login_session['html_course'], 
			students = html_student, links = getProfessorLinks(course_id))



@app.route('/professor/profile')
def showProfessorProfile():
    if 'username' not in login_session:
        return redirect('/login')
    return render_template('profProfile.html', current_courses = login_session['html_course'])



@app.route('/professor/feedback')
def showProfessorFeedback():
    if 'username' not in login_session:
        return redirect('/login')
    return render_template('profFeedback.html', current_courses = login_session['html_course'])

#for students

@app.route('/student/feedback')
def showStudentFeedback():
    return render_template('studentFeedback.html')

@app.route('/student/search')
def showStudentSearch():
    return render_template('studentSearch.html')

@app.route('/student/content')
def showStudentContent():
    return render_template('studentContent.html')

@app.route('/student/announcement')
def showStudentAnnouncement():
    return render_template('studentAnnouncement.html')

@app.route('/student/profile')
def showStudentProfile():
    return render_template('studentProfile.html')



