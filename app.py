from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import login, db, connect_db, User, Topic, UserTopic, Post, Subreddit, TopicSubreddit, HotPost
from forms import LoginForm,  SignupForm
from flask_login import current_user, login_user, login_required, logout_user
import os

app = Flask(__name__)
login.init_app(app)
login.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///reddit"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gotmynews1')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


# # =============================================================================

@app.route('/')
def root():
    """Show home page"""
    if current_user.is_authenticated:
        return redirect('/posts')

    return render_template('home.html')


  
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if current_user.is_authenticated:
        return redirect('/posts')
    
    form = SignupForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user is None:
            user = User(
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                email=form.email.data,
                
            )

            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return redirect("/topics")

        flash('A user already exists with that email address.')
        return render_template('users/signup.html', form=form)

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if current_user.is_authenticated:
        return redirect('/posts')

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(password=form.password.data):
            login_user(user)
            flash(f"Hello, {user.first_name}!")
            return redirect('/posts')
        else:
            flash("Invalid email/password")
            return render_template('users/login.html', form=form)
            
    else:
        return render_template('users/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/topics', methods=['POST', 'GET'])
@login_required
def show_topics():
    """Show all available topics"""
    
    if request.method == 'POST':

        topics_ids = request.form.getlist('user_topic')

        if len(topics_ids) is not 0:

            for topic_id in topics_ids:
    
                user_topic = UserTopic(
                user_id=current_user.id,
                topic_id= topic_id     
                )

                db.session.add(user_topic)
                db.session.commit()

            return redirect('/posts')

        flash("Pick at least one topic")
        return redirect('/topics')
        
    return render_template('users/topics.html')

@app.route('/posts')
@login_required
def posts():
    """Shows weekly hot posts for current user based on their topics"""

    cur_user = User.query.get(f"{current_user.id}")
    cur_user_topics = cur_user.topics
    cur_user_topic_ids = [t.id for t in cur_user_topics]

    posts = HotPost.query.filter(HotPost.topic_id.in_(cur_user_topic_ids)).order_by(HotPost.date.desc()).limit(9).all()

    return render_template('posts.html', posts=posts)