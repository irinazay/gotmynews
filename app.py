from flask import Flask, request, redirect, render_template, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from models import db, connect_db, User, Topic, UserTopic, Post, Subreddit, TopicSubreddit
from forms import LoginForm,  SignupForm
import os

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
  
  return render_template("404.html"), 404

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

    if "firstname" in session:
        return redirect(f"/users/{session['firstname']}/posts")

    return render_template('home.html')


  
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if "firstname" in session:
        return redirect(f"/users/{session['firstname']}/posts")
    
    form = SignupForm()
    selected_topics = session['topics']

    if form.validate_on_submit():
        email_lowercase = (form.email.data).strip().lower()

        existing_user = User.query.filter_by(email=email_lowercase).first()
        
        if existing_user is None:
            user = User(
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                email=email_lowercase,
                
            )
            
            user.set_password(form.password.data)
            db.session.add(user)
            session.pop("topics")
            db.session.commit()  # Create new user
            session['firstname'] = user.first_name  # Log in as newly created user
    
            if len( selected_topics) != 0:
                for x in range(7):
                    topic = str(x+1)
                    if topic in selected_topics:
                        user_topic = UserTopic(
                        user_id=user.id,
                        topic_id= x+1,
                        isSelected=True    
                )
                        db.session.add(user_topic)
                        db.session.commit()
                    else:
                        user_topic = UserTopic(
                        user_id=user.id,
                        topic_id= x+1,
                        isSelected=False   
                )
                        db.session.add(user_topic)
                        db.session.commit()
            
            return redirect(f"/users/{user.first_name}/posts")

        flash('A user already exists with that email address.')
        return render_template('users/signup.html', form=form)

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if "firstname" in session:
        return redirect(f"/users/{session['firstname']}/posts")

    form = LoginForm()

    if form.validate_on_submit():

        email_lowercase = (form.email.data).strip().lower()
        user = User.query.filter_by(email=email_lowercase).first()

        if user and user.check_password(password=form.password.data):
            session['firstname'] = user.first_name
            return redirect(f"/users/{user.first_name}/posts")
        else:
            flash("Invalid email/password")
            return render_template('users/login.html', form=form)
            
    return render_template('users/login.html', form=form)



@app.route('/logout')
def logout():
    session.pop("firstname")
    return redirect("/login")


@app.route('/topics', methods=['POST', 'GET'])
def show_topics():
    """Show all available topics"""

    if request.method == 'POST':

        topics_ids = request.form.getlist('topic')

        if len(topics_ids) != 0:
            session['topics'] = topics_ids
            return redirect('/signup')

        flash("Pick at least one topic")
        return redirect('/topics')
        
    return render_template('topics.html')

@app.route("/users/<firstname>/posts")
def posts(firstname):
    """Shows weekly hot posts for current user based on their topics"""

    if "firstname" not in session or firstname != session['firstname']:
        raise Unauthorized()
    user = User.query.filter_by(first_name=firstname).one()
    curr_user_topics = UserTopic.query.filter_by(user_id=user.id,isSelected=True).all()
    subreddit_ids = [s.topic_id for s in curr_user_topics]
    

    if len(subreddit_ids) != 0:
        
        posts = []
        
        for curr_sub_id in subreddit_ids:
            
            post = Post.query.filter_by(subreddit_id=curr_sub_id).order_by(Post.date.desc()).limit(9).all()
            if len(post) != 0:
                posts.append(post[0])
            
        return render_template('users/posts.html', posts=posts)

    return redirect('/')


@app.route('/users/<firstname>/topics', methods=['POST', 'GET'])
def show_users_topics(firstname):
    """Show all user's topics"""

    if "firstname" not in session or firstname != session['firstname']:
        raise Unauthorized()
    user = User.query.filter_by(first_name=firstname).one()

    curr_user_topics = UserTopic.query.filter_by(user_id=user.id,isSelected=True).all()
    topics = [s.topic_id for s in curr_user_topics]

    if request.method == 'POST': 

        topics_ids = request.form.getlist('selected_topic')

        if len(topics_ids) != 0:
            for x in range(7):
                topic = str(x+1)
                if topic in topics_ids:
                    user_topic =  UserTopic.query.filter_by(user_id=user.id, topic_id=x+1).one()
                    user_topic.isSelected = True 
                    db.session.commit()
                else:
                    user_topic =  UserTopic.query.filter_by(user_id=user.id, topic_id=x+1).one()
                    user_topic.isSelected = False 
                    db.session.commit() 

        return redirect(f"/users/{session['firstname']}/posts")

    return render_template('users/topics.html',topics=topics)