from flask import Flask, render_template, flash, session, request, redirect
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import yaml
import os

blog = Flask(__name__)
Bootstrap(blog)
db = yaml.load(open('db.yaml'))

# Configuring database
blog.config['MYSQL_HOST'] = db['mysql_host']
blog.config['MYSQL_USER'] = db['mysql_user']
blog.config['MYSQL_PASSWORD'] = db['mysql_password']
blog.config['MYSQL_DB'] = db['mysql_db']
blog.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(blog)
blog.config['SECRET_KEY'] = os.urandom(24)

CKEditor(blog)


# Home Page
@blog.route('/', methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    resultValue = cur.execute('SELECT * FROM blog')
    if resultValue > 0:
        blogs = cur.fetchall()
        cur.close()
        return render_template('index.html', blogs=blogs)
    cur.close()
    return render_template('index.html', blogs=None)


# Registration Page
@blog.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Password do not match !', 'danger')
            return render_template('register.html')
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO user(first_name, last_name, username, email, password) VALUES(%s,%s,%s,%s,%s)',
                    (userDetails['first_name'], userDetails['last_name'], userDetails['username'], userDetails['email'],
                     generate_password_hash(userDetails['password'])))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successful ! Please Login.', 'success')
        return redirect('/login')
    return render_template('register.html')


# Login Page
@blog.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        cur = mysql.connection.cursor()
        resultValue = cur.execute('SELECT * FROM user WHERE username = %s', ([username]))
        if resultValue > 0:
            user = cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('Welcome ' + session['first_name'] + ' ! You have successfully logged in.', 'success')
            else:
                cur.close()
                flash('Password do not match', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')


# Writing the blog
@blog.route('/write-blog/', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        blogspot = request.form
        title = blogspot['title']
        body = blogspot['body']
        author = session['first_name'] + ' ' + session['last_name']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO blog(title,body,author) VALUES(%s,%s,%s)', (title, body, author))
        mysql.connection.commit()
        cur.close()
        flash('Blog successfully posted !', 'success')
        return redirect('/')
    return render_template('write-blog.html')


@blog.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute('SELECT * FROM blog WHERE blog_id = {}'.format(id))
    if resultValue > 0:
        blog = cur.fetchone()
        return render_template('blogs.html', blog=blog)
    return 'Blog not found'


if __name__ == '__main__':
    blog.run(debug=True)
