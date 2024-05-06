# Twtiter Clone (CSCI143)
## By: My Nguyen

[![](https://github.com/myngpog/cs143-final/actions/workflows/tests.yml/badge.svg)](https://github.com/myngpog/cs143-final/actions/workflows/tests.yml)

[Final Exam Link Details](https://github.com/mikeizbicki/cmc-csci143/tree/2024spring/topic_13_finalproject)

### Overview
This is a basic, working version of twitter. It includes the use of Python, Flask, HTML/CSS, Jinja2, and SQLite3. 

### Functionalities include:
**Task 1:** The project structure should follow the structure of the [flask-on-docker homework](https://github.com/mikeizbicki/cmc-csci143/tree/2024spring/topic_03_instagram_tech_stack#homework).  In particular:
1. There should be a development `docker-compose.yml` file with a web service and postgres service.
1. There should be a production `docker-compose.yml` file with a web service, postgres service, and nginx service.
1. You should be able to start your web page by running `docker-compose up` with either of these yml files.
1. You must have appropriate volumes defined so that bringing the containers down does not delete the database.
1. You must store all (non-sensitive) project files in a git repo.
    It should be trivial to bring your project up/down from only the files in the repo.
1. You must create your own github actions test case that:
    1. builds the containers,
    1. brings the containers up,
    1. loads test data into the database,
    1. and passes (i.e. turns green) only when there are no errors in this process.


**Task 2:** You must design a database.
1. The schema file should
    1. be located in `services/postgres/schema.sql`.
    1. be loaded automatically into the database on startup
    1. contain at least 3 tables, each of which has:
        1. a primary key
        1. at least 2 columns with appropriate types and constraints
        1. appropriate indexes

        > **Hint:**
        > The easiest database to build would be based on the `pg_normalized` database, with the `tweets`, `users`, and `urls` tables.

        > **Important:**
        > All indexes that you will need for making your routes fast must be included in the `schema.sql` file.

1. You should have a script that loads test data into the database.  After running the script:
    1. Every table should have at least 1,000,000 rows
    1. At least one table must have 10,000,000 rows

**Task 3-8:** The remaining 6 tasks each correspond to an individual route on your webpage.

*Route `/`*
1. a link to this page should always be visible in your menu, whether the user is logged in or not logged in
1. this route displays all the messages in the system
1. the messages should be ordered chronologically with the most recent message at the top
1. each message should include the user account that created it, the time of creation, and the message contents
1. you should display only the most recent 20 messages, and there should be links at the bottom that will take you to previous messages

*Route `/login`*
1. a link to this page should only be visible in your menu if the user is not logged in
1. this route will present a form for the user to enter their username/password;
   the password box must not display the user's password as they are typing it in

1. you must display appropriate error messages if the user enters an incorrect username/password
1. after a user successfully logs in, you must automatically redirect them to the homepage


*Route `/logout`*
1. a link to this page should only be visible if the user is logged in
1. this route will delete the cookies that the log in form creates, logging the user out

*Route `/create_account`*
1. a link to this page should only be visible in your menu if the user is not logged in
1. if the user attempts to create an account that already exists, they should get an appropriate error message
1. the user should be prompted to enter their password twice; if the passwords do not match, they should get an appropriate error message

*Route `/create_message`*
1. a link to this page should only be visible in your menu if the user is logged in
1. the user must be able to enter whatever message body they want,
   but you will also need to store the user id of the user that created a message and the time the message was created
1. you will only get credit for this route if the message correctly shows up on the home route after creation

*Route `/search`* **(new)**
1. a link to this page should always be visible
1. the user should be given an input field to enter a search query
1. after the search query has been entered, a FTS should be performed over the messages, and the results returned in a format similar to the home (`/`) route
1. if many messages match search pattern, then the resulting messages must have next/previous buttons to traverse the pages
1. for full credit on this route:
    1. you must use a RUM index instead of a GIN index for the FTS
    1. you must order the results by most relevancy
    1. you must highlight search terms that match the query


### Build Instructions
To build:
```
# Build
docker-compose up -d --build

# Take down
docker-compose down

# Take down volumes as well 
docker-compose down -v
```

