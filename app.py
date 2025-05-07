from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/blog_platform'
db = SQLAlchemy(app)

from models import Post

# Создан маршрут для инициализации базы данных
@app.route('/init-db')
def init_db():
    db.create_all()
    return 'Database initialized!'

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)