# Cybersecurity Project

This application is ment to demonstrate several cyber security flaws from the 2017 OWASP top 10 list.
Entering any private information is not adviced!

## Users in the database

|Username | Password |
|---------|----------|
|admin    | admin    |
|alice    | redqueen |
|bob      | squarepants|
|john     | qwerty   |

## Flaw Descriptions 

### SQL injection

The registration function from views.py contains a raw sql query, which makes the application vulnerable to SQL injections:

query = "SELECT id FROM auth_user WHERE username='%s'" % (usrn)
response = cursor.execute(query).fetchall()

To test an injection go to the registration form and enter the following to the username field:

bob' UNION SELECT creditcard FROM pages_account WHERE id=2; --

you will see the result of the injection on the bottom of the register page. To not add sql query usernames to the database one can purposefully enter mismatching passwords. 

### Broken Access Control

The user can upload textfiles to their account. These files are accessible and uploadable to all other users if they manipulate the url.

Let’s say that alice uploads a file with the id = 1. If then bob visits the url “http://127.0.0.1:8000/download/1”, he has access to the file which alice has uploaded and can upload it to himself. 

### Broken authentication

In the database in the table pages_userinfo, where all the users, their passwords and admin status are stored without encryption. Also is the user john with an easy to crack password in the system (qwerty). Also, the admin user has weak authentication credentials (username: admin, password: admin).  

### Cross-site Scripting (XSS)

There is an unprotected message field on the application, where one can put code, such as javascript. It is for example possible to steal the victims csfrtoken and session id. 

### Sensitive Data Exposure

The user’s personal information is available to attackers on several different levels: the database contains nonencrypted passwords and creditcard numbers vulnerable to sql injections, the user’s personal files are available to download through url manipulation.

