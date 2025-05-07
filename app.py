from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/blog_platform'
db = SQLAlchemy(app)

from models import Post, User, Category

# Create a route to initialize the database
@app.route('/init-db')

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

if __name__ == '__main__':
    app.run(debug=True)