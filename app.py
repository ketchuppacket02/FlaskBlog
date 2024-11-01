import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'



# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

#function to retrieve a post from db
def get_post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)
    return post


# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    #get a connection to the database
    conn =get_db_connection()

    #execute a query to read all posts from the post table in the database
    posts = conn.execute('SELECT * FROM posts').fetchall()

    #close the connection
    conn.close()

    #send the posts to index.html template to be displayed
    return render_template('index.html',posts=posts)


# route to create a post
@app.route('/create/', methods=('GET','POST'))
def create():
    #determine if the page is being requesred with a POST or GET request

    if request.method == 'POST':
        #get the title and content that was submitted
        title = request.form['title']
        content = request.form['content']

        #display error message if title or content is not submitted
        #else make a database connection and insert the blog post content
        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()
            #insert data into database
            conn.execute('INSERT INTO posts (title, content) VALUES (?,?)', (title,content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

#create a route to edi a post. Load page with get or post method
@app.route('/<int:id>/edit/', methods=('GET','POST'))
def edit(id):
    #get the post from the database with a select query or the post with that id
    post = get_post(id)


    #determine if the page is being requested with a POST or GET
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
    
        #if not title or content, flash error message
        if not title:
            flash('Title is required')
        elif not content:
            flash('Content is required')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    #if GET display the page
    return render_template('edit.html', post=post)

from flask import url_for, redirect, flash

@app.route('/<int:id>/delete/', methods=('POST',))
def delete_post(id):
    # Retrieve the post to ensure it exists
    post = get_post(id)

    # Connect to the database and delete the post
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Flash a success message and redirect to the homepage
    flash('"{}" was deleted successfully!'.format(post['title']))

    #redirect to homepage
    return redirect(url_for('index'))



app.run(port=5000)