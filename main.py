from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy #Ist this needed?

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:3306/build-a-blog' 
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# First, set up the blog so that the "add a new post" form and the blog listings are on the same page, as 
# with Get It Done!, and then separate those portions into separate routes, handler classes, and templates. 
# For the moment, when a user submits a new post, redirect them to the main blog page.

#The /blog route displays all the blog posts.

#You're able to submit a new post at the /newpost route. After submitting a new post, your app displays the 
#main blog page.

#You have two templates, one each for the /blog (main blog listings) and /newpost (post new blog entry) views.
# Your templates should extend a base.html template which includes some boilerplate HTML that will be used on each page.

#In your base.html template, you have some navigation links that link to the main blog page and to the add new blog page.

#If either the blog title or blog body is left empty in the new post form, the form is rendered again, with a helpful
#error message and any previously-entered content in the same form inputs.




# Blog class with the necessary properties (i.e., an id, title, and body
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))#Is this long enough?
    #completed = db.Column(db.Boolean)

    def __init__(self, title):
        self.title = name
        self.completed = False #Is this needed?


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title, blog_body)


        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all() #Modified since there is no completed field - Blog.query.filter_by(completed=False).all()
    #Not using this field with blogs completed_blogs = Blog.query.filter_by(completed=True).all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs) #Not using with blogs completed_blogs=completed_blogs)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    #Not using with blogs blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()