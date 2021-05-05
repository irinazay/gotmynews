from models import db, connect_db, User, Topic, UserTopic, Post, Subreddit, TopicSubreddit, HotPost
from app import app
import requests
import time
from sqlalchemy import func, desc
from secrets import REDDIT_REFRESH_TOKEN, USER_CREDENTIALS

# using SendGrid's Python Library https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import urllib.request as urllib
import ssl
from jinja2 import Environment, FileSystemLoader

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


# sub = Subreddit.query.all()
# subreddits = [s.url for s in sub]

# resp = requests.post('https://www.reddit.com/api/v1/access_token', 
# headers={'Authorization': f'Basic {USER_CREDENTIALS}',
# 'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'},
# params={"grant_type": "refresh_token",
# "refresh_token": REDDIT_REFRESH_TOKEN
# })


# data = resp.json()


# refresh_token = data['access_token']

# for subreddit in subreddits:
        
#         resp = requests.get(f"https://oauth.reddit.com/{subreddit}/hot", 
#         headers={'Authorization': f'Bearer {refresh_token}',
#         'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'},
#         params={"limit": 1})

        
#         data = resp.json()

#         score = data['data']['children'][0]['data']['score']
#         title = data['data']['children'][0]['data']['title']
#         url = data['data']['children'][0]['data']['permalink']

#         sub = Subreddit.query.filter_by(url=f"{subreddit}").one()

#         post = Post(
#             score=score,
#             url=url,
#             title=title,
#             subreddit_id=sub.id       
#         )

#         db.session.add(post)
#         time.sleep(5)

#         db.session.commit()


# sub = Subreddit.query.all()
# subreddit_ids = [s.id for s in sub]

# for sub_id in subreddit_ids:

#     hottest_post_by_subreddit_id = Post.query.filter_by(subreddit_id = f"{sub_id}").order_by(Post.score.desc()).limit(1).one()
    

#     top = TopicSubreddit.query.filter_by(subreddit_id=f"{sub_id}").one()
#     title = hottest_post_by_subreddit_id.title
#     url = hottest_post_by_subreddit_id.url
    

#     hot_post = HotPost(
#         url=url,
#         title=title,
#         topic_id=top.topic_id       
#     )

#     db.session.add(hot_post)
# #     db.session.commit()
  

users = User.query.all()
for user in users:
    
    user_topics = user.topics
    user_topic_ids = [t.id for t in user_topics]
    posts = HotPost.query.filter(HotPost.topic_id.in_(user_topic_ids)).order_by(HotPost.date.desc()).limit(9).all()
    html_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html data-editor-version="2" class="sg-campaigns" xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">
      <meta http-equiv="X-UA-Compatible" content="IE=Edge">
      <style type="text/css">
    body, p, div {
      font-family: verdana,geneva,sans-serif;
      font-size: 16px;
    }
    body {
      color: #000000;
    }
    body a {
      color: #ff4500;
      text-decoration: none;
    }
    }
  </style>
    </head>

    <body>
      <center class="wrapper" data-link-color="#ff4500" data-body-style="font-size:16px; font-family:verdana,geneva,sans-serif; color:#000000; background-color:#fff;">
        <div class="webkit">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" class="wrapper" bgcolor="#fff">
            <tr>
              <td valign="top" bgcolor="#fff" width="100%">
                <table width="100%" role="content-container" class="outer" align="center" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td width="100%">
                      <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td>
                                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:600px;" align="center">
                                      <tr>
                                        <td role="modules-container" style="padding:0px 0px 0px 0px; color:#000000; text-align:left;" bgcolor="#F9F5F2" width="100%" align="left"><table class="module preheader preheader-hide" role="module" data-type="preheader" border="0" cellpadding="0" cellspacing="0" width="100%" style="display: none !important; mso-hide: all; visibility: hidden; opacity: 0; color: transparent; height: 0; width: 0;">
    <tr>
      <td role="module-content">
        <p></p>
      </td>
    </tr>
  </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="c67d6467-f76e-4a00-87dc-e80f267cb3bd" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:18px 0px 18px 0px; line-height:40px; text-align:inherit; background-color:#C3F53C;" height="100%" valign="top" bgcolor="#C3F53C" role="module-content"><div><h1 style="text-align: center">gotmynews</h1><div></div></div></td>
      </tr>
    </tbody>
  </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="8VquPM2ZMj7RJRhAUE6wmF" data-mc-module-version="2019-10-22">
      <tbody><tr>
        <td style="background-color:#C3F53C; padding:20px 0px 10px 0px; line-height:30px; text-align:inherit;" height="100%" valign="top" bgcolor="#C3F53C"><div><div style="font-family: inherit; text-align: center"><span style="font-size: 24px; font-family: georgia, serif; color: #ff4500"><strong>Recent posts you might find valuable based on your interests:</strong></span><span style="color: #516775; font-size: 28px; font-family: georgia, serif"><strong>&nbsp;</strong></span></div><div></div></div></td>
      </tr>
    </tbody></table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="keQHYG1b1ztewxwhDtuCpS" data-mc-module-version="2019-10-22">
      <tbody><tr>
        <td style="background-color:#C3F53C; padding:10px 40px 20px 40px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="#C3F53C"><div><div style="font-family: inherit; text-align: center"><br></div>
  <ul>"""

    for post in posts:
      html_text += "<li><a href='" 'http://reddit.com' + post.url + "'>" + post.title + "</a></li>"  

    html_text += """
</ul>
 
<div style="font-family: verdana, geneva, sans-serif; text-align: inherit"><br></div><div></div></div></td>
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

    message = Mail(from_email, to_email, subject, html_content)

    try: 
      response = sendgrid_client.send(message=message)
      print(response.status_code)
      print(response.body)
      print(response.headers)
    except urllib.HTTPError as e:
      print(e.read())
      exit()
