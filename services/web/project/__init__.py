import os
import re

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    make_response,
    render_template,
    redirect,
    url_for,
    Markup
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import sqlalchemy
from sqlalchemy import text
from time import time

# for db connection efficiency
from contextlib import contextmanager


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod"

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
    """
    Helper function to check if the username and password can be found in the database
    """
    sql = """
    SELECT screen_name, password
    FROM users
    WHERE screen_name = :username AND
          password = :password
    LIMIT 1;
    """
    with get_connection() as connection:
        result = connection.execute(sqlalchemy.text(sql), {"username": username, "password": password}).fetchone()
        return result is not None  # if result is not none, then it returns true, otherwise, it returns false


def displayTweets():
    # render_template does preprocessing of the input html file;
    # technically, the input to the render_template function is in a language called jinja2
    # the output of render_template is html

    # display newest 20 tweets
    messages = [{}]

    sql = """
    SELECT tweets.id_users, users.screen_name as username, tweets.text, tweets.created_at
    FROM tweets
    JOIN users ON tweets.id_users = users.id_users
    ORDER BY tweets.created_at DESC
    LIMIT :limit OFFSET :offset;
    """
    page = request.args.get('page', 1, type=int)
    messages_per_page = 20
    offset = (page - 1) * messages_per_page
    with get_connection() as connection:
        result = connection.execute(text(sql), {'limit': messages_per_page, 'offset': offset}).fetchall()
        for row in result:
            messages.append({
                'username': row.username,
                'text': row.text,
                'created_at': row.created_at.strftime('%Y-%m-%d %H:%M:%S')  # .strftime is to format date for better readability
            })
    return messages, page


@app.route('/')
def root():
    print_debug_info()

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)
    messages, page = displayTweets()

    return render_template('root.html', logged_in=good_credentials, messages=messages, page=page)


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
    message = request.args.get('message', default=None)

    # the first time we've visited, no form submission

    if username is None:
        return render_template('login.html', bad_credentials=False, message=message)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            # return 'login successful'

            # create a cookie that contains the username/password info

            template = render_template(
                'login.html',
                bad_credentials=False,
                logged_in=True)
            # return template
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


@app.route('/search', methods=['GET', 'POST'])
def search():
    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    messages = [{}]
    page = request.args.get('page', 1, type=int)
    num_messages = 20
    offset = (page - 1) * num_messages

    if request.method == 'GET':
        keyword = request.args.get('search')
        if keyword:
            with get_connection() as connection:
                formatted_keyword = ' '.join(keyword.strip().split())
                print(formatted_keyword)
                sql = """
                SELECT tweets.text AS text, users.screen_name, tweets.created_at
                FROM tweets
                JOIN users USING (id_users)
                WHERE to_tsvector('english', tweets.text) @@ phraseto_tsquery(:keyword)
                ORDER BY to_tsvector('english', tweets.text) <=> phraseto_tsquery(:keyword), created_at DESC, id_tweets DESC
                LIMIT :limit OFFSET :offset;
                """

                start_time = time()
                results = connection.execute(text(sql), {'limit': num_messages, 'offset': offset, 'keyword': f'{formatted_keyword}'})
                execution_time = time() - start_time
                regex = re.compile(re.escape(keyword), re.IGNORECASE)  # highlighting assist
                for row in results:
                    highlighted_text = Markup(regex.sub(lambda match: f'<mark>{match.group(0)}</mark>', row.text))  # highlighting assist
                    messages.append({'text': highlighted_text, 'created_at': row.created_at, 'screen_name': row.screen_name})

                print(f"Query Execution Time: {execution_time:.2f} seconds")  # Print execution time

                # Check if messages are empty and return appropriate response
                if all(not d for d in messages):
                    print("messages list is empty")
                    messages = False
                    return render_template('search.html', logged_in=good_credentials, messages=messages, searched=True, no_results="No tweets found", page=page)

                print("successful print")
                return render_template('search.html', logged_in=good_credentials, messages=messages, searched=True, page=page)

    return render_template('search.html', logged_in=good_credentials, searched=False)


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
    This function is a helper function for create_message that gets the user id associated with the account that made the tweet
    """
    with get_connection() as connection:
        result = connection.execute(text("SELECT id_users FROM users WHERE screen_name = :username"), {'username': username})
        # fetch the first column of the row (user id)
        user_id = result.scalar()
        return user_id


def is_valid_username(username):
    """
    Function that only makes it possible to create usernames that are valid with existing Twitter guidelines (from ChatGPT)
    """
    # Regular expression to check if the username is valid
    # This regex allows only alphanumeric characters and underscores, and limits the length to 15 characters.
    if re.match(r'^\w{1,15}$', username):
        return True
    else:
        return False


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    """
    Inserts user account info into the users table
    """
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        passwordCheck = request.form["retype_password"]

        # checks if username input field is empty
        if not username:
            print("empty username field!")
            return render_template('create_user.html', returnMessage="Brevity is key, but maybe have something.")

        # checks if the username is valid
        if not is_valid_username(username):
            print("invalid username")
            return render_template('create_user.html', returnMessage="Invalid characters in username")

        if password != passwordCheck:
            print("passwords don't match")
            return render_template('create_user.html', returnMessage="Passwords do not match.")

        with get_connection() as connection:
            transaction = connection.begin()
            # Check if the username already exists in the database
            existing_user = connection.execute(
                sqlalchemy.text("SELECT screen_name FROM users WHERE screen_name = :username"),
                {'username': username}
            ).fetchone()

            # if existing user alreayd exists
            if existing_user:
                return render_template('create_user.html', returnMessage="Username already exists.")

            # If checks pass, insert new user
            try:
                sql = """
                INSERT INTO users (
                    created_at,
                    screen_name,
                    password
                ) VALUES (
                    NOW(),
                    :username,
                    :password
                );
                """
                connection.execute(sqlalchemy.text(sql), {'username': username, 'password': password})
                transaction.commit()
                return redirect(url_for('login', message='Account created successfully. Please login'))
            except Exception as e:
                print("An error occurred:", e)
                return render_template('create_user.html', returnMessage=str(e))

    return render_template('create_user.html')
