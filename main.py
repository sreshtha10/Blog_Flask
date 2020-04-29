from flask import Flask, render_template, flash, session, request, redirect
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
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


# Home Page
@blog.route('/',methods = ['GET','POST'])
def index():
    return render_template('index.html')


# Registration Page
@blog.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method is 'POST':
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


# About Page
@blog.route('/about/')
def about():
    return render_template('about.html')


# Blog
@blog.route('/blogs/<int:id>/')
def blogs(id):
    return render_template('blog.html', blog_id=id)


# Login Page
@blog.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@blog.route('/write-blog/', methods=['GET', 'POST'])
def write_blog():
    return render_template('write-blog.html')


@blog.route('/my-blog/')
def my_blog():
    return render_template('my-blog.html')


@blog.route('/edit/<int:id>/', methods=['GET', 'POST'])
def edit(id):
    return render_template('edit.html', blog_id=id)


@blog.route('/delete-blog/<int:id>/', methods=['POST'])
def delete(id):
    return render_template('delete-blog.html', blog_id=id)


@blog.route('/logout/')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    blog.run(debug=True)
