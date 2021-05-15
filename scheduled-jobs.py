
from models import db, connect_db, User, Topic, UserTopic, Post, Subreddit, TopicSubreddit
from app import app
import requests
import time
from sqlalchemy import desc
from dotenv import load_dotenv
from flask_script import Manager

# using SendGrid's Python Library https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import urllib.request as urllib
import ssl

# take environment variables from .env.
load_dotenv()
# define script commands
manager = Manager(app)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


@manager.command
def posts():
    # Requesting a new access token using a refresh token
    REDDIT_REFRESH_TOKEN = os.environ.get('REDDIT_REFRESH_TOKEN')
    USER_CREDENTIALS = os.environ.get('USER_CREDENTIALS')

    resp = requests.post('https://www.reddit.com/api/v1/access_token', 
    headers={'Authorization': f'Basic {USER_CREDENTIALS}',
    'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'},
    params={"grant_type": "refresh_token", "refresh_token": REDDIT_REFRESH_TOKEN})

    data = resp.json()
    refresh_token = data['access_token']


    # Making daily requests to reddit's API to get one hot post per every predetermed subreddit
    sub = Subreddit.query.all()
    subreddits = [s.url for s in sub]
    for subreddit in subreddits:
        
        resp = requests.get(f"https://oauth.reddit.com/{subreddit}/top", 
        headers={'Authorization': f'Bearer {refresh_token}',
        'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'},
        params={"limit": 1, "t": "week"})

        
        data = resp.json()

        title = data['data']['children'][0]['data']['title']
        url = data['data']['children'][0]['data']['permalink']

        sub = Subreddit.query.filter_by(url=f"{subreddit}").one()

        post = Post(
            url=url,
            title=title,
            subreddit_id=sub.id       
        )

        db.session.add(post)
        time.sleep(5)

        db.session.commit()


@manager.command
def emails():

    users = User.query.all()
    for user in users:
    
        user_topics = user.topics
        posts= []
        for user_topic in user_topics:
          user_subreddits = user_topic.subreddits
          user_subreddits_ids = [s.id for s in user_subreddits]
          post = Post.query.filter(Post.subreddit_id.in_(user_subreddits_ids)).order_by(Post.date.desc()).limit(9).all()
          posts.append(post[0])


        html_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html data-editor-version="2" class="sg-campaigns" xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">
      <meta http-equiv="X-UA-Compatible" content="IE=Edge">
      <style type="text/css"></style>
    </head>

    <body>
      <center class="wrapper" data-body-style="font-size:16px; color:#000000; background-color:#fff;">
        <div class="webkit">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" class="wrapper">
            <tr>
              <td valign="top" width="100%">
                <table width="100%" role="content-container" class="outer" align="center" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td width="100%">
                      <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td>
                                    <table width="80%" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:600px;" align="center">
                                      <tr>
                                        <td role="modules-container" style="padding:0px 0px 0px 0px; color:#000000; text-align:left;" bgcolor="#F9F5F2" width="100%" align="left"><table class="module preheader preheader-hide" role="module" data-type="preheader" border="0" cellpadding="0" cellspacing="0" width="100%" style="display: none !important; mso-hide: all; visibility: hidden; opacity: 0; color: transparent; height: 0; width: 0;">
   
  </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="c67d6467-f76e-4a00-87dc-e80f267cb3bd" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:10px 0px 10px 0px; line-height:40px; text-align:inherit; background-color:#C3F53C;" height="100%" valign="top"" role="module-content"><div><h1 style="text-align: center; font-family: 'Roboto Mono', monospace;">GOTMYNEWS</h1></div></td>
      </tr>
    </tbody>
  </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="8VquPM2ZMj7RJRhAUE6wmF" data-mc-module-version="2019-10-22">
      <tbody><tr>
        <td style="background-color:#C3F53C; padding:20px 10px 10px 0px; text-align:inherit;" height="100%" valign="top"><div style=" text-align: center"><span style="font-size: 18px; font-family: 'Roboto Mono', monospace; color: #000"><strong>Recent posts you might find valuable:</strong></span></div></td>
      </tr>
    </tbody></table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="keQHYG1b1ztewxwhDtuCpS" data-mc-module-version="2019-10-22">
      <tbody><tr>
        <td style="background-color:#C3F53C; padding:0px 10px 0px 15px;" height="100%" valign="top"><div>
  
  
  <div style="font-size:17px; font-family: 'Roboto Mono', monospace; ">
  <ul>"""

        for post in posts:
            html_text += "<li style='margin: 15px;'><a href='" 'http://reddit.com' + post.url + "'>" + post.title + "</a></li>"  

        html_text += """
 </ul>
 </div>

</td>
      </tr>
    </tbody></table><div data-role="module-unsubscribe" class="module unsubscribe-css__unsubscribe___2CDlR" role="module" data-type="unsubscribe" style="background-color:#fbfcfc; color:#444444; font-size:12px; line-height:20px; padding:16px 16px 16px 16px; text-align:center;" data-muid="mQ1u1Awkou7szvSGChCGcV"><p style="font-family:arial,helvetica,sans-serif; font-size:12px; line-height:20px;"><a class="Unsubscribe--unsubscribeLink" href="{{{unsubscribe}}}" style="">Unsubscribe</a> - <a href="{{{unsubscribe_preferences}}}" target="_blank" class="Unsubscribe--unsubscribePreferences" style="">Unsubscribe Preferences</a></p></div></td>
                                      </tr>
                                    </table>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </div>
      </center>
    </body>
  </html>"""

        sendgrid_client = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = From("noreply@irinazaytseva.com", 'Gotmynews')
        to_email = To(f"{user.email}")
        subject = Subject("Your weekly posts")
        html_content = HtmlContent(html_text)
        print(html_content)

        message = Mail(from_email, to_email, subject, html_content)

        try: 
            response = sendgrid_client.send(message=message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except urllib.HTTPError as e:
            print(e.read())
            exit()

if __name__ == "__main__":
    manager.run()