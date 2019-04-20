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


@app.route('/blog', methods=['POST'])
def blog():
    return render_template("blog.html")

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == "POST":
        blog_title = request.form["title"]
        new_title = Blog(blog_title)
        db.session.add(new_title)
        blog_body = request.form["body"]
        new_body = Blog(blog_body)
        db.session.add(new_body)
        db.session.commit()

    return render_template("newpost.html")


if __name__ == '__main__':
    app.run()