from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import login, db, connect_db, User, Topic, UserTopic, Post, Subreddit, TopicSubreddit
from forms import LoginForm,  SignupForm
from flask_login import current_user, login_user, login_required, logout_user
import os

app = Flask(__name__)
login.init_app(app)
login.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgres:///gotmynews").replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gotmynews1')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

app.app_context().push()
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
    selected_topics = session['topics']
    print("================================")
    print(selected_topics)
    if form.validate_on_submit():
        email_lowercase = (form.email.data).strip().lower()
        print("================================")
        print(email_lowercase)
        existing_user = User.query.filter_by(email=email_lowercase).first()
        
        if user: 
            return redirect('/signup')
        if existing_user is None:
            user = User(
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                email=email_lowercase,
                
            )
            
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            # print("logining user")
            # login_user(user)  # Log in as newly created user
            # print("inserting selected topics")
            if len( selected_topics) != 0:
                for x in range(7):
                    topic = str(x+1)

                    if topic in selected_topics:
                        user_topic = UserTopic(
                        user_id=current_user.id,
                        topic_id= x+1,
                        isSelected=True    
                )
                        db.session.add(user_topic)
                        db.session.commit()
                    else:
                        user_topic = UserTopic(
                        user_id=current_user.id,
                        topic_id= x+1,
                        isSelected=False   
                )

                        db.session.add(user_topic)
                        db.session.commit()
            
            return redirect("/posts")

        flash('A user already exists with that email address.')
        return render_template('users/signup.html', form=form)

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    print("is current user is authenticated")
    print(current_user)
    if current_user.is_authenticated:
        return redirect('/posts')

    form = LoginForm()
    print("======================")
    print(form.email.data)
    if form.validate_on_submit():

        email_lowercase = (form.email.data).strip().lower()
        user = User.query.filter_by(email=email_lowercase).first()

        if user and user.check_password(password=form.password.data):
            # login_user(user)
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
def show_topics():
    """Show all available topics"""

    if request.method == 'POST':

        topics_ids = request.form.getlist('user_topic')

        if len(topics_ids) != 0:
            session['topics'] = topics_ids
            return redirect('/signup')

        flash("Pick at least one topic")
        return redirect('/topics')
        
    return render_template('users/topics.html')

@app.route('/posts')
@login_required
def posts():
    """Shows weekly hot posts for current user based on their topics"""
    
    curr_user_topics = UserTopic.query.filter_by(user_id=current_user.id,isSelected=True).all()
    subreddit_ids = [s.topic_id for s in curr_user_topics]
    

    if len(subreddit_ids) != 0:
        
        posts = []
        
        for curr_sub_id in subreddit_ids:
            
            post = Post.query.filter_by(subreddit_id=curr_sub_id).order_by(Post.date.desc()).limit(9).all()
            if len(post) != 0:
                posts.append(post[0])
            
        return render_template('posts.html', posts=posts)

    return redirect('/topics')

@app.route('/user/topics', methods=['POST', 'GET'])
@login_required
def show_users_topics():
    """Show all user's topics"""
    print("================================/user/topics")
    print(current_user)
    curr_user_topics = UserTopic.query.filter_by(user_id=current_user.id,isSelected=True).all()
    topics = [s.topic_id for s in curr_user_topics]

    if request.method == 'POST': 

        topics_ids = request.form.getlist('user_topic')

        if len(topics_ids) != 0:
            for x in range(7):
                topic = str(x+1)
                if topic in topics_ids:
                    user_topic =  UserTopic.query.filter_by(user_id=current_user.id, topic_id=x+1).one()
                    user_topic.isSelected = True 
                    db.session.commit()
                else:
                    user_topic =  UserTopic.query.filter_by(user_id=current_user.id, topic_id=x+1).one()
                    user_topic.isSelected = False 
                    db.session.commit() 

        return redirect('/posts')
    return render_template('users/topics.html',topics=topics)