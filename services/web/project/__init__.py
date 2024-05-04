import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    make_response,
    render_template,
    redirect,
    url_for
    # bcrypt
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import sqlalchemy
from sqlalchemy import text

# for db connection efficiency
from contextlib import contextmanager


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev"

# Tutorial's table // DEAD CODE
class User(db.Model):

    __tablename__ = "users_b"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@contextmanager
def get_connection():
    """
    This function helps build the connection with the databases so SQL commands can run, then finally, it closes the connection.
    """
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    # FIXME:
    # look inside the databasse and check if the password is correct for the user
    if username == 'haxor' and password == '1337':
        return True
    else:
        return False

def displayTweets():
    # render_template does preprocessing of the input html file;
    # technically, the input to the render_template function is in a language called jinja2
    # the output of render_template is html

    # display newest 20 tweets
    messages = [{}]

    sql = """
    SELECT tweets.id_users, users.name as username, tweets.text, tweets.created_at
    FROM tweets
    JOIN users ON tweets.id_users = users.id_users
    ORDER BY tweets.created_at DESC
    LIMIT 20;
    """
    with get_connection() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        for row in result:
            messages.append({
                'username': row.username,
                'text': row.text, 
                'created_at': row.created_at.strftime('%Y-%m-%d %H:%M:%S') # .strftime is to format date for better readability
            })
    return messages

@app.route('/')     
def root():
    print_debug_info()

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials) 

    return render_template('root.html', logged_in=good_credentials, messages=displayTweets())


@app.route('/login', methods=['GET', 'POST'])     
def login():
    print_debug_info()
    # requests (plural) library for downloading;
    # now we need request singular 
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            #return 'login successful'

            # create a cookie that contains the username/password info

            template = render_template(
                'login.html', 
                bad_credentials=False,
                logged_in=True)
            #return template
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response

@app.route('/logout')     
def logout():
    # Clear the login cookies by setting an empty value and an expiry time in the past
    response = make_response(render_template('logout.html', logged_in=False))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('user_id', '', expires=0)

    return response

# 403 error code

@app.route('/search', methods=['GET', 'POST'])
def search():
    keyWord = request.args.get('search')

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    return render_template('search.html', logged_in=good_credentials)

@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # create message
    if request.method == 'POST':
        # removes trailing and ending whitespaces to check for empty input
        message = request.form.get('message').strip() if request.form.get('message') else ''
        print(message)
        if not message:  # No message was entered
           return render_template('create_message.html', returnMessage="No message provided.", logged_in=good_credentials)

        try:
            with get_connection() as connection:
                transaction = connection.begin()
                try:
                    id_users = get_user_id(username)
                    print(id_users)
                    sql = """
                    INSERT INTO tweets (
                        id_users,
                        created_at, 
                        text
                    ) VALUES (
                        :id_users, 
                        NOW(), 
                        :message);
                    """
                    print("Executing SQL...")
                    connection.execute(text(sql), {'id_users': id_users, 'message': message})
                    transaction.commit()
                    print("SQL executed successfully.")
                    # in case of error in trans
                except Exception as e:    
                    transaction.rollback()
                    raise e
            return render_template('create_message.html', returnMessage="Message successfully posted!", logged_in=good_credentials)
            
        # in case of error with connection
        except Exception as e:
            print("An error occurred:", e)
            return render_template('create_message.html', returnMessage=str(e), logged_in=good_credentials)   
    
    return render_template('create_message.html', logged_in=good_credentials)


def get_user_id(username):
    """
    This function is a helper function for create_message that 
    """
    with get_connection() as connection:
        result = connection.execute(text("SELECT id_users FROM users WHERE name = :username"), {'username': username})
        # fetch the first column of the row (user id)
        user_id = result.scalar()
        return user_id
    

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    return render_template('create_user.html')

#     username = request.form.get('username')
#     password = request.form.get('password')
#     retype_password = request.form.get('retype_password')

#     if password != retype_password:
#             return render_template('create_user.html', error="Passwords do not match.")
    
#     if password != retype_password:
#         return render_template('create_user.html', error="Passwords do not match.")

#     with get_connection() as connection:
#         # Check if username is already taken
#         result = connection.execute(text("SELECT id_users FROM users WHERE name = :username"), {'username': username})
#         # checks the database to see if username exists in it 
#         user_exists = result.scalar()
#         if user_exists:
#             return render_template('create_user.html', error="Username already taken.")

#         # Insert new user
#         password_hash = hash_password(password)
#         sql = """
#         INSERT INTO users (created_at, name, password_hash) VALUES (NOW(), :username, :password_hash)
#         """
#         connection.execute(text(sql), {'username': username, 'password_hash': password_hash})
#         return redirect(url_for('login'))  # Redirect to a login page after account creation

# # Helper functions to hash passwords before storing them in a database
# def hash_password(password):
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# def check_password(provided_password, stored_hash):
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)
