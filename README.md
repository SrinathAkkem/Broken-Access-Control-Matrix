# Cybersecurity Project

This application demonstrates 5 cybersecurity flaws from the 2017 OWASP top 10 list.

The project has been created using python3. Run 

$ python3 manage.py runserver

to start the application from command line.

It is recommended to create a virtual environment for the project and installing requirements.txt's dependencies. 

$ python3 -m venv venv\
$ sourve venv/bin/activate\
$ pip install -r requirements.txt


## Users in the database

|Username | Password |
|---------|----------|
|admin    | admin    |
|alice    | redqueen |
|bob      | squarepants|
|john     | qwerty   |

## Flaw Descriptions 

### Broken Access Control

#### Description
The user can upload textfiles to their account. These files are accessible and uploadable to all other users if they manipulate the url.

Let’s say that alice uploads a file with the id = 1. If then bob visits the url “http://127.0.0.1:8000/download/1”, he has access to the file which alice has uploaded and can upload it to himself. 

#### How to fix it

restrict access to the file by modifying methods in the views.py as such:

[Link to relevant code](https://github.com/ssuihko/cybersecurityproject/blob/9f8595baed255b86b14a1e2a46deb85711ef405e/pages/views.py#L40)

```
def downloadView(request, fileid): 				
	...						
	f = File.objects.get(pk=fileid)			
	if f.owner != request.user:				
		return redirect(‘/’)					
	…						
```

This code checks the user’s id everytime they attempt to download a file, so access to files which are not theirs is cut off. 


### Broken authentication

#### Description
In the database in the table pages_userinfo, where all the users, their passwords and admin status are stored without encryption. Also is the user john with an easy to crack password in the system (qwerty). The admin user has weak authentication credentials (username: admin, password: admin). The register page allows users to create accounts with weak credentials. According to the OWASP Top 10 list, weak credentials are a broken authentication security vulnerability, since attackers can, with sufficient scanning, break into accounts with bruteforce. 

#### How to fix it
If admin creates users, they should primarily be created from the admin view by launching the app and entering http://127.0.0.1:8000/admin and logging in as the admin user. Creating new users this way will automatically encrypt the password, and the system will refuse creating too easy to guess passwords.

The register function should be modified:

[Link to relevant code](https://github.com/ssuihko/cybersecurityproject/blob/9f8595baed255b86b14a1e2a46deb85711ef405e/pages/views.py#L90)

```
def register(request):

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), '../db.sqlite3')
form = UserCreationForm(request.POST)

if request.method == 'POST':

…
	if form.is_valid():
	    form.save()
	    user = authenticate(username=usrn, password=pw1)
		if user is not None:
			account = Account.objects.create(owner=user, points=request.POST.get('points'), iban=request.POST.get('iban'), creditcard=request.POST.get('creditcard'))
			userinfo = Userinfo.objects.create(name=usrn, password=pw1, admin=0)
				return redirect('/')
	else:
	    form = UserCreationForm()
return render(request, 'pages/register.html', {'form': form})
```

The form adds validation to the register form from the settings.py’s
AUTH_PASSWORD_VALIDATORS. 

### Cross-site Scripting (XSS)

#### Description
There is an unprotected message field on the application, where one can put code, such as javascript. It is for example possible to steal the victims csfrtoken and session id. This can be demonstrated by entering a following message:

```javascript
<script>
var xhr = new XMLHttpRequest();
xhr.open("POST", /mail/, true);
xhr.setRequestHeader('Content-Type', 'application/json')
xhr.send(JSON.stringify({content: document.cookie}));
</script>
```

The targets csrftoken and session id get stolen whenever the victim views his or her accounts homepage and its messages. This can be seen from the console.

#### How to fix it
One option is to sanitize the output in the index.html file using django framework’s autoescape feature like this:

[Link to relevant code](https://github.com/ssuihko/cybersecurityproject/blob/9f8595baed255b86b14a1e2a46deb85711ef405e/pages/templates/pages/index.html#L51)

```
...
{% for msg in msgs %}

<i>From {{msg.source.username}} to {{msg.target.username}}</i></br>
{% autoescape on %}
{{msg.content}}
{% endautoescape %}
</br>
</br>

…
```

When autoescaping is in effect, variable content has HTML escaping applied to it. This means that characters such as <, >, “, & get encoded to HTML. Now the xss attack above does not work anymore. (check the console)

### Sensitive Data Exposure

#### Description
The user’s personal information is available to attackers on several different levels: the database contains nonencrypted passwords and creditcard numbers vulnerable to sql injections.

Now let’s see how this application is vulnerable to sensitive data exposure through sql injection in practice.

Go to the register site. Type this into the usernamefield (to avoid actually adding a user in the database with an injection as a username, one can enter mismatching passwords on purpose. Register button will still execute the sql injection query. Do not leave iban or creditcard field empty.)

bob' UNION SELECT creditcard FROM pages_account WHERE id=2; -- 
bob' UNION SELECT password FROM pages_userinfo WHERE name='alice 

See the bottom of the registration page. The message will normally only display the username which is already in use, but now the message displays another message with the credit card number/password as well. 

#### How to fix it

The requested solution to this flaw will require resetting the database. 

One possible way is to make the Userinfo table’s password field and Account table’s credit card field encrypted by modifying the models. There are many existing python django libraries which can be installed with pip and used to encrypt fields so that the data is only decrypted when retrieved properly from the database. Here's one example:

[Link to relevant code](https://github.com/ssuihko/cybersecurityproject/blob/9f8595baed255b86b14a1e2a46deb85711ef405e/pages/models.py#L5)

models:py

```
from django_cryptography.fields import encrypt

class Account(models.Model):
owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
iban = models.IntegerField()
creditcard = encrypt(models.CharField(max_length=200))

…

class Userinfo(models.Model):
name = models.CharField(max_length=200)
password = encrypt(models.CharField(max_length=200))
admin = models.IntegerField()
```

After this delete 0001_initial.py and db.sqlite3 files. Run commands:\
$ python3 manage.py migrate\
$ python3 manage.py makemigrations pages\
$ python3 manage.py sqlmigrate pages 0001\
$ python3 manage.py migrate\
$ python3 manage.py createsuperuser

Then create a new user/s in the registration page. (Choosing username bob will make copypasting sql injections above easier.)

Now the retrieved data from the sql injections above should should be in an encrypted form.

### SQL injection

#### Description
The registration function from views.py contains a raw sql query, which makes the application vulnerable to SQL injections:

```
query = "SELECT id FROM auth_user WHERE username='%s'" % (usrn)
response = cursor.execute(query).fetchall()
```

To test an injection go to the registration form and enter the following to the username field:

bob' UNION SELECT creditcard FROM pages_account WHERE id=2; --

you will see the result of the injection on the bottom of the register page. To not add sql query usernames to the database one can purposefully enter mismatching passwords. 

#### How to fix it

[Link to relevant code](https://github.com/ssuihko/cybersecurityproject/blob/9f8595baed255b86b14a1e2a46deb85711ef405e/pages/views.py#L101)

Option 1:

modify views.py's register function cursor.execute query:

```
response = cursor.execute("SELECT username FROM auth_user WHERE username=?", (usrn,)).fetchall()
```

Option 2:
Remove the raw query from registration on views.py. To check out wether a username already exists within the database one can use code like this instead:

```
query = User.objects.filter(username=usrn).exists()

if query is True or pw1 != pw2:
	if pw1 != pw2:
		messages.error(request, ‘The passwords didn’t match!’)
	else:
		messages.error(request, ‘username ’ + usrn + ‘ is already in use’)
	return redirect('/register')
```

The already existing username should be taken from the usrn parameter, not the query. 
