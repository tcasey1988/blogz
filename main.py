from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'signup', 'list_blogs']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('viewpost.html', title='Post', post=post)
        
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs, title='Build a Blog')

@app.route('/newpost')
def new_post():
    return render_template('newpost.html', title='Add a New Entry')

@app.route('/newpost', methods=['POST', 'GET'])
def submit_post():
    title_name = request.form['title']
    body_name = request.form['body']

    title_error = ''
    body_error = ''

    if title_name == '':
        title_error = 'Not a valid title'

    if body_name == '':
        body_error = 'Not a valid body'

    if not title_error and not body_error:
        new_entry = Blog(title_name, body_name)
        db.session.add(new_entry)  
        db.session.commit()
        post_id = Blog.query.filter_by(title=title_name).first().id
        return redirect('/blog?id={0}'.format(post_id))
    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error, title='Build a Blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user'] = user.email
            flash('Logged In')
            return redirect('/newpost')
        else:
            if not user:
                flash('Incorrect username')
                return redirect('/login')
            elif user.password != password:
                flash('Incorrect password')
                return redirect('/login')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if email == "" or password == "" or verify == "":
            flash('One or more fields invalid')
            return redirect('/signup')

        if password != verify:
            flash('Passwords do not match')
            return redirect('/signup')

        if len(email) < 3:
            flash('Invalid email')
            return redirect('/signup')

        if len(password) < 3:
            flash('Invalid password')
            return redirect('/signup')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists')
            return redirect('/signup')
        
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/login')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()