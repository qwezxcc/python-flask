from flask import Flask 
from flask import request, session, redirect, url_for, flash
from flask import render_template
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# == База даних  ====================================
app.config['SECRET_KEY'] = "my_sekret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'ari.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "please login to acces the page"
login_manager.login_message_category = 'warning'

# == моделі бази даних ==
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=0)

class News(db.Model):   
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# == ROUTE =============================================================

@app.route('/')
def index():    
    return render_template('index.html', title="main")

@app.route('/about')
def about():
    return render_template('about.html', title="credits")

# --- БЛОК АВТОРИЗАЦІЇ ---
@app.route('/login', methods=['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"user: {user.username}", 'success')
            return redirect(url_for('index'))
        else:
            flash("wrong username or password. try again.", 'error')
           
    return render_template('login.html', title="login page")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get("password")
        # print(username, email, password)

        email_exists = User.query.filter_by(email=email).first()

        if email_exists:
            flash("user with this email already exists")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()

        flash('register success! now you can login.', 'success')
        return redirect(url_for('login'))
    
    # відкрити сторінку реєстрації
    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    # вихід з системи
    logout_user()
    flash("logout complete.", 'success')
    return redirect(url_for('index'))



# --- СТОРІНКИ для авторизованих користувачів

@app.route('/news')
@login_required
def news():
    all_news = News.query.order_by(News.date_posted.desc()).all()
    return render_template("news.html", all_news=all_news)

@app.route('/my_library')
@login_required
def my_library():
    return render_template("my_library.html")

@app.route('/addnews' , methods=['GET', 'POST'])
@login_required
def addnews():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        
        new_post = News(title=title, content=content, author_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash("new", 'success')
        return redirect(url_for('news'))
    #smth

    return render_template("addnews.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



if __name__ == "__main__":
    with app.app_context():
        db.create_all()   

    app.run(debug=True)

