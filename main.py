from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi, re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:3306/blogz' 
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'y234kGL569'

#Use Case 1: We click on a blog entry's title on the main page and go to a blog's individual entry page.

#Use Case 2: After adding a new blog post, instead of going back to the main page, we go to that blog post's 
#individual entry page.

"""More use cases
User enters a username that is stored in the database with the correct password and is redirected to the /newpost page with their username being stored in a session.
User enters a username that is stored in the database with an incorrect password and is redirected to the /login page with a message that their password is incorrect.
User tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.

For /login page:

User enters a username that is stored in the database with the correct password and is redirected to the /newpost page with their username being stored in a session.
User enters a username that is stored in the database with an incorrect password and is redirected to the /login page with a message that their password is incorrect.
User tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.
User does not have an account and clicks "Create Account" and is directed to the /signup page.
For /signup page:

User enters new, valid username, a valid password, and verifies password correctly and is redirected to the '/newpost' page with their username being stored in a session.
User leaves any of the username, password, or verify fields blank and gets an error message that one or more fields are invalid.
User enters a username that already exists and gets an error message that username already exists.
User enters different strings into the password and verify fields and gets an error message that the passwords do not match.
User enters a password or username less than 3 characters long and gets either an invalid username or an invalid password message.

User is logged in and adds a new blog post, then is redirected to a page featuring the individual blog entry they just created (as in Build-a-Blog).
User visits the /blog page and sees a list of all blog entries by all users.
User clicks on the title of a blog entry on the /blog page and lands on the individual blog entry page.
User clicks "Logout" and is redirected to the /blog page and is unable to access the /newpost page (is redirected to /login page instead).

User is on the / page ("Home" page) and clicks on an author's username in the list and lands on the individual blog user's page.
User is on the /blog page and clicks on the author's username in the tagline and lands on the individual blog user's page.
User is on the individual entry page (e.g., /blog?id=1) and clicks on the author's username in the tagline and lands on the individual blog user's page.
"""


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50)) #Normally should not store in DB but per assignment is OK to do here
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User does not exist', 'error')
        elif user.password != password:
            flash('User password incorrect', 'error')
        else:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost') #('/')
            
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # Validate user's entries
        if username == "":
            username_error = "Invalid username (left blank)"
        elif len(username) < 3:
            username_error = "Username must be at least 3 characters long."
        
        if password == "":
            password_error = "Invalid password (left blank)"
        elif len(password) < 3:
            password_error = "Password must be at least 3 characters long."

        if verify == "":
            verify_error = "Invalid re-entered password (left blank)."
        elif password != verify:
            password_error = "Passwords must match."
            verify_error = password_error

        if (username_error or password_error or verify_error):
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error)
        else:
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                username_error = "Username already exists."
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost') 


        if (username_error or password_error or verify_error):
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error) #could improve this
        else:
            return render_template('signup.html') #Might need to add error encoded error etc.

    return render_template('signup.html') #Might need to add error encoded error etc.


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title="Build a Blog User List", users=users)


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    bid = request.args.get('id')
    buser = request.args.get('user')


    if bid is None:
        if buser is None:
            blogs = Blog.query.all()
            return render_template('blog.html', title="Build a Blog", blogs=blogs)
        else:
            blogs = Blog.query.filter_by(owner_id=buser).all()
            return render_template('blog.html', title="Build a Blog", blogs=blogs)
    else:
        blogs = Blog.query.filter_by(id=bid).all()
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error=""
    body_error=""

    if request.method == 'POST':

        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if blog_title == "":
            title_error="Please enter a title."
        
        if blog_body == "":
            body_error="Please enter a blog body."
        
        if not(title_error or body_error):
            owner = User.query.filter_by(username=session['username']).first()
    
            new_blog = Blog(blog_title, blog_body, owner)

            db.session.add(new_blog)
            db.session.commit()
            
            bid = new_blog.id

    else:   
        return render_template('newpost.html', title='Add a New Blog Entry')

    if (title_error or body_error):
        return render_template('newpost.html', title='Add a New Blog Entry', title_error=title_error, body_error=body_error)

    else:
        return redirect('/blog?id={0}'.format(bid) )


if __name__ == '__main__':
    app.run()