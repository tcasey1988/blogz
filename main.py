from flask import Flask, request, redirect, render_template, session, flash, url_for
from app import app, db
from models import User, Blog
from hashutils import check_pw_hash

app.secret_key = 'secretkey'

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'signup', 'list_blogs', 'home', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('viewpost.html', title='Post', header='Blog posts!', post=post)

    if request.args.get('user'):
        user = request.args.get('user')
        user_id = User.query.filter_by(username=user).first().id
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', title='User', header='Blog posts!', posts=posts)
        
    blogs = Blog.query.all()
    return render_template('blog.html', title='Blog Posts', header='All blog posts!', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def submit_post():
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        owner = User.query.filter_by(username=session['user']).first()
        
        if title_name == '':
            flash('Not a valid title', 'error')
            return redirect('/newpost')

        if body_name == '':
            flash('Not a valid body', 'error')
            return redirect('/newpost')

        new_entry = Blog(title_name, body_name, owner)
        db.session.add(new_entry)  
        db.session.commit()
        post_id = Blog.query.filter_by(title=title_name).first().id
        return redirect('/blog?id={0}'.format(post_id))

    return render_template('newpost.html', title='New Post', header='Add a new post')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=user).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['user'] = user.username
            flash('Logged In')
            return redirect('/newpost')
        else:
            if not user:
                flash('Incorrect username', 'error')
                return redirect('/login')
            elif user.password != password:
                flash('Incorrect password', 'error')
                return redirect('/login')

    return render_template('login.html', title='Login Page', header='Login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if user == '' or password == '' or verify == '':
            flash('One or more fields invalid', 'error')
            return redirect('/signup')

        if password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')

        if len(user) < 3:
            flash('Invalid username', 'error')
            return redirect('/signup')

        if len(password) < 3:
            flash('Invalid password', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=user).first()
        if existing_user:
            flash('User already exists', 'error')
            return redirect('/signup')
        
        user = User(username=user, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect('/newpost')

    return render_template('signup.html', title='Create User', header='Signup')

@app.route('/')
def home():
    users = User.query.all()
    return render_template('index.html', title='Blogz', header='All blog users!', users=users)

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()