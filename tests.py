from unittest import TestCase
from app import app
from models import db, User, Post, Topic, UserTopic, Subreddit, TopicSubreddit, HotPost
from flask_login import current_user

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///reddit_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


db.create_all()


class UserTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user."""
        
        # app.config['LOGIN_DISABLED'] = True

        db.drop_all()
        db.create_all()

        user = User(last_name="Zaytseva", first_name="Irina", email="irinavzaytseva@gmail.com", password_hash="password")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        topic = Topic(name="Test_topic")
        db.session.add(topic)
        db.session.commit()
        self.topic_id = topic.id

        subreddit = Subreddit(url="r/subreddit")
        db.session.add(subreddit)
        db.session.commit()
        self.subreddit_id = subreddit.id

        topic_subreddit = TopicSubreddit(topic_id=self.topic_id, subreddit_id=self.subreddit_id)
        db.session.add(topic_subreddit)
        db.session.commit()
 
        user_topic = UserTopic(topic_id=self.topic_id, user_id=self.user_id)
        db.session.add(user_topic)
        db.session.commit()


        post = Post(title="testtitle", url="r/subreddit", score= 55, subreddit_id=self.subreddit_id)
        db.session.add(post)
        db.session.commit()
       

        hotpost = HotPost(title="testtitle", url="r/subreddit", topic_id=self.topic_id)
        db.session.add(hotpost)
        db.session.commit()
      
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_home_page(self):
        with app.test_client() as c:
            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create Your Own Reddit Newsletters Within Minutes</h1>', html)
 

    def test_signup(self):
       
        with app.test_client() as c:
               
            data = { "last_name": "Zaytseva", "first_name":"Irina", "email":"testname@gmail.com", "password_hash": "password"}
            
            resp = c.post("/signup", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            

    def test_login(self):

        with app.test_client() as c:
            

            data = { "email": 'irinavzaytseva@gmail.com', "password": 'password' }
            resp = c.post("/login", data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(current_user.first_name,'James')
            


    def test_valid_signup(self):
        user = User(id = 2, last_name="Test", first_name="Test", email="testtest@test.com", password_hash="password")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        u_test = User.query.get(self.user_id)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password_hash, "ggggg")


    def test_show_topics(self):


        with app.test_client() as c:
            data = { "email": 'irinavzaytseva@gmail.com', "password": 'password' }
            resp = c.post("/login", data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(current_user.first_name,'James')
            
            # resp = c.get("/topics", follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 200)
            # self.assertIn('<h2>Please select as many topics as you like:</h2>', html)



    def test_add_zero_topics(self):
        # when user doesn't pick any topic    
        with app.test_client() as c:

                resp = c.post("/topics", follow_redirects=True)
                html = resp.get_data(as_text=True)        
                self.assertEqual(resp.status_code, 200)
                # self.assertIn('<h2>Please select as many topics as you like:</h2>', html)
                



    # def test_add_one_or_more_topics(self):
    #     # when user pick one or more topic    
    #     with app.test_client() as c:

    #             user = User(last_name="Test", first_name="Test", email="test@test.com", password_hash="password")
    #             db.session.add(user)
    #             db.session.commit()
    #             current_user = user
    #             self.user_id = user.id

    #             self.assertTrue(current_user.email == 'test@test.com')
    #             data = { "user_topic": self.topic_id}
                  
    #             resp = c.post("/topics", data=data, follow_redirects=True)
    #             html = resp.get_data(as_text=True)        
    #             self.assertEqual(resp.status_code, 200)
    #             self.assertIn('<p class="posts_lists">Recent Posts you might find valuable based on your interests:</p>', html)


    # def test_posts(self):

    #     user_topic = UserTopic(topic_id=self.topic_id, user_id=current_user.id)
    #     db.session.add(user_topic)
    #     db.session.commit() 
    #     with app.test_client() as c:
    #         resp = c.get("/posts", current_user=current_user)
    #         html = resp.get_data(as_text=True)        
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<p class="posts_lists">Recent Posts you might find valuable based on your interests:</p>', html)
                
            
