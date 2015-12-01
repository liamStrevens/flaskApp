
from flask import Flask, flash, session, request, redirect, url_for, render_template
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import dbConnect
import string
import random
from flask_mail import Mail, Message


config = {'DB_HOST':'LiamStrevens.mysql.pythonanywhere-services.com','DB_USER':'LiamStrevens','DB_PASSWD':'Passw0rd1','DB_NAME':'LiamStrevens$flask_app'}


app = Flask(__name__)
mail=Mail(app)

app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=587,
	MAIL_USE_TLS=True,
	MAIL_USERNAME = 'flaskappauto@gmail.com',
	MAIL_PASSWORD = 'test1234567'
	)

mail=Mail(app)
def sendEmail(email, username):
    randomword = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    randomword = username + randomword
    sqlCommand = """update users set regString = '{0}' where name = '{1}'""".format(randomword,username)
    with dbConnect.dbConnecting(config) as cursor:
        cursor.execute(sqlCommand)
    try:
        msg = Message(
            'Email confirmation',
	        sender='flaskappauto@gmail.com',
	        recipients= [email])

        msg.body = "http://liamstrevens.pythonanywhere.com/regConfirm/" + randomword
        mail.send(msg)

        return "render_template('index.html')"
    except SMTPException as e:
        print('exception test failed')
        return 'test'

def check_login(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged_in_user' in session:
            return func(*args, **kwargs)
        elif 'logged_in_admin' in session:
            return func(*args, **kwargs)
        flash('You are not logged in')
        return redirect(url_for('login_page'))
    return wrapped_function

def check_admin_login(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):

        if 'logged_in_admin' in session:
            return func(*args, **kwargs)
        elif 'logged_in_user' in session:

            flash('you do not have rights to enter this page')
            return redirect(url_for('login_page'))
        else:
            flash('You are not logged in')
            return redirect(url_for('login_page'))
    return wrapped_function

@app.route('/regConfirm/<id>')
def confirm(id):

    sqlCommand = """select * from users where regString = '{0}'""".format(id)
    print(sqlCommand)
    with dbConnect.dbConnecting(config) as cursor:
        cursor.execute(sqlCommand)

        result = cursor.fetchone()
        if result is None:
            return 'an error'
        else:
            sqlCommand = """update users set registered = 1 where name = '{0}'""".format(result[1])
            with dbConnect.dbConnecting(config) as cursor:
                cursor.execute(sqlCommand)
                flash('sucessfully registered')
                return redirect(url_for('login_page'))





@app.route('/')
def start_page():
    return render_template('index.html')
@app.route('/index')
def index_page():
    return render_template('index.html')

@app.route('/Login',methods=['POST','GET'])
def login_page():

    if request.method == 'GET':
        return render_template('Login.html')
    else:
        the_username = request.form['username']
        the_password = request.form['password']
        sqlCommand = """select * from users where name = '{0}' or email = '{0}'""".format(the_username)
        print(sqlCommand)
        with dbConnect.dbConnecting(config) as cursor:
            cursor.execute(sqlCommand)

            result = cursor.fetchone()

            if result is None:
                flash('username doesnt exist')
                return redirect(url_for('login_page'))
            else:
                if result[5] == 1:
                    if check_password_hash(result[2],the_password) is True:
                        if result[4] == 'user':
                            session.clear()
                            session['logged_in_user'] = True
                            flash('normal log in')
                            return redirect(url_for('start_page'))
                        elif result[4] == 'Administrator':
                            session.clear()
                            session['logged_in_admin'] = True
                            flash('Admin log in')
                            return redirect(url_for('start_page'))
                    flash('Incorrect password')
                    return redirect(url_for('login_page'))
                else:
                    flash('Please verify your email')
                    return redirect(url_for('login_page'))





@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        the_username = request.form['username']
        the_password = generate_password_hash(request.form['password'])
        the_email = request.form['email']
        the_type = request.form['type']
        sqlCommand = """select * from users where name = '{0}' or email = '{1}'""".format(the_username , the_email)
        with dbConnect.dbConnecting(config) as cursor:
            cursor.execute(sqlCommand)

            result = cursor.fetchone()

            if result is None:
                sqlCommand = """insert into users (name,password,email,user_type) values ('{0}','{1}','{2}','{3}')""".format(the_username,the_password, the_email,the_type)
                print(sqlCommand)
                with dbConnect.dbConnecting(config) as cursor:
                    cursor.execute(sqlCommand)
                sendEmail(the_email,the_username)
                flash('Please check your email to confirm registration')
                return redirect(url_for('index_page'))
            else:
                flash('username or email already exists already exists')
                return redirect(url_for('register'))

@app.route('/logout',methods=['POST','GET'])
@check_login
def logout():
    session.clear()
    flash('Logged out sucessfully')
    return redirect(url_for('start_page'))


@app.route('/userPage',methods=['POST','GET'])
@check_login
def logged_in_user():
    return render_template('userPage.html')


@app.route('/AdminPage',methods=['POST','GET'])
@check_admin_login
def logged_in_admin():
    return render_template('AdminPage.html')
app.secret_key = 'Youwillguess'

if __name__ == "__main__":
    app.run(debug=True)