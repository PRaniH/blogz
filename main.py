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


if __name__ == '__main__':
    app.run()