from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi, re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:3306/build-a-blog' 
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

#ASSIGNMENT...displays blog posts on a main page and allows users to add new blog posts on a form page. After submitting a 
#new blog entry on the form page, the user is redirected to a page that displays only that blog (rather than 
#returning to the form page or to the main page). Each blog post has a title and a body. 

#Make sure you can say the following about your app:

#The /blog route displays all the blog posts.

#You're able to submit a new post at the /newpost route. After submitting a new post, your app displays the 
#main blog page.

#You have two templates, one each for the /blog (main blog listings) and /newpost (post new blog entry) views.
#Your templates should extend a base.html template which includes some boilerplate HTML that will be used on each page.

#In your base.html template, you have some navigation links that link to the main blog page and to the add new blog page.

#If either the blog title or blog body is left empty in the new post form, the form is rendered again, with a helpful
#error message and any previously-entered content in the same form inputs.

#Let's add the ability to view each blog all by itself on a webpage. Instead of creating multiple HTML files, 
#one for each new blog post we create, we can use a single template to display a given blog's title and body.
#We'll designate which blog's data we want displayed by using a query param containing the id for that blog in the url. 
#Then the request handler can dynamically grab the blog that corresponds to that id from the database and pass it to 
#the template to generate the desired page.

#There are two use cases for this functionality:

#Use Case 1: We click on a blog entry's title on the main page and go to a blog's individual entry page.

#Use Case 2: After adding a new blog post, instead of going back to the main page, we go to that blog post's 
#individual entry page.
#For both use cases we need to create the template for the page that will display an individual blog, so start 
#by making that. All it needs do is display a blog title and blog body. 



# Blog class with the necessary properties (i.e., an id, title, and body)
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.owner = owner #Doesn't need to say owner_id?

""" User class and associated table to our app. It should have the following properties:

id which is an Integer primary key that auto-increments (just like the others you've created in class)
username which will be a String with a size of your choosing
password which will also be a String with a size of your choosing
blogs which signifies a relationship between the blog table and this user, thus binding this user with the blog posts they write."""

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    passowrd = db.Column(db.String(50)) #Normally should not store in DB but per assignment is OK to do here
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, username, password): #Need to add blogs in here?
        self.username = username
        self.password = password

#Copied below from sample code


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost') #('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

#TO DO User enters a username that is stored in the database with an incorrect password and is redirected to the /login page with a message that their password is incorrect.
#TO DO User tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.
#TO DO User does not have an account and clicks "Create Account" and is directed to the /signup page.
    return render_template('login.html')

#Do we need the below?
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#TO DO Note several reqs. for the below, review later
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost') #('/') 
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


"""One of the first and easiest changes is to make the header 
for the blog title on the home page be a link. But what url do 
we want it to link to? Well, this is the format that we want the 
url of a single blog entry to have: ./blog?id=6 (Here 6 is just 
one example of an id number for a blog post.) So using jinja2 
templating syntax, how can you make sure that each blog entry 
that is generated on the main page has an href with a query
parameter corresponding to its id?

The next thing we need to determine is how we are going to handle
an additional GET request on our homepage since we are already
handling a GET request there. Of course, the difference is that
in this use case it's a GET request with query parameters. So
we'll want to handle the GET requests differently, returning 
a different template, depending on the contents (or lack 
thereof) of the dictionary request.args.

Finally, we need to think about how the template is going to know 
which blog's data to display. The blog object will be passed into 
the template via render_template. What are the steps we need to take 
to get the right blog object (the one that has the id we'll get from 
the url) from the database and into the render_template function call?"""


@app.route('/', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)


@app.route('/blog', methods=['POST', 'GET'])
def index():
    bid = request.args.get('id')

    if bid is None:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs)
    else:
        blogs = Blog.query.filter_by(id=bid).all()
        return render_template('blog.html', blogs=blogs)


#You've got to create a new database record for the blog entry that has just been submitted, but
#before redirecting, you need to grab the id for the record you just created. That way you'll 
#know what url (i.e., what number to put on the right side of ?id=) to redirect the user to after 
#they submit their new entry.
#When you create a new blog post object, it doesn't immediately have an id that is not None. 
#However, after running db.session.commit(), SQLAlchemy will populate the id property of the 
#object to be the value auto-generated by the database upon insert. In other words, after you 
#commit, you can get the id by using the id property of the object you just saved.

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
            new_blog = Blog(blog_title, blog_body)
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