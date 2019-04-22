from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost')
def new_post():
    return render_template('newpost.html', title="Add a New Entry")

@app.route('/blog', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs, title="Build a Blog")

@app.route('/newpost', methods=['POST', 'GET'])
def submit_post():
    title_name = request.form['title']
    body_name = request.form['body']

    title_error = ""
    body_error = ""

    if title_name == "":
        title_error = "Not a valid title"
    else:
        title_name = title_name

    if body_name == "":
        body_error = "Not a valid body"
    else:
        body_name = body_name

    if not title_error and not body_error:
        new_entry = Blog(title_name, body_name)
        db.session.add(new_entry)  
        db.session.commit()
        return redirect("/blog")
    else:
        return render_template("newpost.html", title_error=title_error, body_error=body_error, title="Build a Blog")
    
if __name__ == '__main__':
    app.run()