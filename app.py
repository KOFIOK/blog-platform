from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/blog_platform'
app.config['SECRET_KEY'] = 'a_very_secure_secret_key_for_blog_platform'  # Безопасный ASCII ключ
db = SQLAlchemy(app)

# Настройка Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from models import Post, User, Category, Comment, Like
from forms import RegistrationForm, LoginForm, CommentForm

# Create a route to initialize the database
@app.route('/init-db')
def init_db():
    db.create_all()
    return 'Database initialized!'

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(
                content=form.content.data,
                post_id=post.id,
                user_id=current_user.id
            )
            db.session.add(comment)
            db.session.commit()
            flash('Ваш комментарий добавлен!', 'success')
            return redirect(url_for('post', post_id=post.id))
        else:
            flash('Для добавления комментариев необходимо войти в систему', 'info')
            return redirect(url_for('login'))
    
    # Получаем комментарии для поста, отсортированные по дате (новые сверху)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    
    return render_template('post.html', post=post, form=form, comments=comments)

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Проверяем, поставил ли пользователь уже лайк этому посту
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()
    
    if existing_like:
        # Если лайк уже поставлен - удаляем его (отмена лайка)
        db.session.delete(existing_like)
        db.session.commit()
        flash('Лайк удален', 'success')
    else:
        # Если лайка нет - добавляем новый
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        flash('Лайк добавлен', 'success')
    
    # Возвращаемся на страницу, с которой пришел запрос
    next_page = request.args.get('next') or request.referrer
    return redirect(next_page or url_for('index'))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Проверка, что текущий пользователь - автор комментария или администратор
    if comment.user_id != current_user.id:
        abort(403)  # Запрещено
    
    post_id = comment.post_id  # Сохраняем id поста перед удалением комментария
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Комментарий удален', 'success')
    return redirect(url_for('post', post_id=post_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Ошибка входа. Проверьте email и пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)