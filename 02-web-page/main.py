from flask import Flask 
from flask import request, session, redirect, url_for, flash
from flask import render_template
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os 

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# == База даних  ====================================
app.config['SECRET_KEY'] = "positions"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ari.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# == моделі бази даних ==
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=0)

with app.app_context():
    db.create_all()
   

# == ROUTE ==========================================
@app.route('/')
def index():    
    return render_template('index.html', title="main")

@app.route('/about')
def about():
    return render_template('about.html', title="credits")

@app.route('/login', methods=['GET', "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            pass

        

    return render_template('login.html', title="login")

@app.route('/login', methods=['POST'])
def login_user():
    
    email = request.form['email']
    password = request.form['password']

    if email == '1@1' and password == '1':
        redirect('/')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        print(username, email, password)

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash("user with this email already exists")
            return redirect(url_for("register"))
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw) 
        db.session.add(new_user)
        db.session.commit()

        flash('acc created! now you can login', 'success')
        return redirect(url_for('login'))

    # open register page
    return render_template('register.html')

@app.route('/news')
def news():
    pass


if __name__ == "__main__":
    app.run(debug=True)
