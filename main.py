from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi, re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:3306/build-a-blog' 
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# ...displays blog posts on a main page and allows users to add new blog posts on a form page. After submitting a 
# new blog entry on the form page, the user is redirected to a page that displays only that blog (rather than 
# returning to the form page or to the main page). Each blog post has a title and a body. 

# Make sure you can say the following about your app:

#The /blog route displays all the blog posts.

#You're able to submit a new post at the /newpost route. After submitting a new post, your app displays the 
#main blog page.

#You have two templates, one each for the /blog (main blog listings) and /newpost (post new blog entry) views.
# Your templates should extend a base.html template which includes some boilerplate HTML that will be used on each page.

#In your base.html template, you have some navigation links that link to the main blog page and to the add new blog page.

#If either the blog title or blog body is left empty in the new post form, the form is rendered again, with a helpful
#error message and any previously-entered content in the same form inputs.

#TO DO Check get and post to see if it's correct

#TO DO Let's add the ability to view each blog all by itself on a webpage. Instead of creating multiple HTML files, 
# one for each new blog post we create, we can use a single template to display a given blog's title and body.
# We'll designate which blog's data we want displayed by using a query param containing the id for that blog in the url. 
# Then the request handler can dynamically grab the blog that corresponds to that id from the database and pass it to 
# the template to generate the desired page.

#There are two use cases for this functionality:

#Use Case 1: We click on a blog entry's title on the main page and go to a blog's individual entry page.

#Use Case 2: After adding a new blog post, instead of going back to the main page, we go to that blog post's 
# individual entry page.
#For both use cases we need to create the template for the page that will display an individual blog, so start 
# by making that. All it need do is display a blog title and blog body. 



# Blog class with the necessary properties (i.e., an id, title, and body)
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    #blog_id = int(request.form['blog-id'])
    #blog = Blog.query.get(blog_id)
    #Not using with blogs blog.completed = True
    
    if request.method == 'POST':

        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title, blog_body)

        db.session.add(new_blog)
        db.session.commit()

    return render_template('newpost.html', title='Add a New Blog Entry') #redirect('/')


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all() 
    
    return render_template('blog.html', title="Build a Blog", blogs=blogs)

#Could the below be combined with /blog route?
@app.route('/', methods=['POST', 'GET'])
def blog():
    title_error=""
    body_error=""

    #blogs = Blog.query.all()

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

    blogs = Blog.query.all()

    if (title_error or body_error):
        return render_template('newpost.html', title='Add a New Blog Entry', title_error=title_error, body_error=body_error)
    else:
        return render_template('blog.html', title="Build a Blog", blogs=blogs)


#def displaypost
#need to ultimately pass in something like http://localhost:5000/hello?first_name=Chris
#like  return redirect("/welcome?username=" + username)
@app.route('/displaypost', methods=['POST', 'GET'])
def displaypost(): #maybe have to get new_blog passed in from new post function?
    #newblog = Blog.query(id=1) #what's the syntax to query what we just added, maybe just need the id?
    blogs = Blog.query.all()
    blogid = str(blogs[3].id) #This is returning the third item in the list. We want the specific one we just created
    #blogid = request.form['blog_id']

    #blogs = Blog.query.get(blogid) #this will give the specific blog asking for
    #db.session.commit() #is this needed to completel the query?

    #How to find the id for the blog we just created?
    

    return redirect("/blogpost?id=" + blogid) #something is off here with how to display the page without .html

@app.route("/blogpost")
def welcome():
    
    #if request.method == "POST":
    #    blogid = request.form['blog']

    blogs = Blog.query.get(17)
    
    #blogid = blogs[3].id
    
    blogtitle = blogs.title
    blogbody = blogs.body

    return render_template('blogpost.html', title=blogtitle, body=blogbody)

    





if __name__ == '__main__':
    app.run()