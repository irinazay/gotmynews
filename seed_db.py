from models import db, Topic, Subreddit

def seed_db():
    # Safety check
    if Topic.query.first():
        print("Database already seeded")
        return

    topics = [
        Topic(id=1, name="Artificial Intelligence"),
        Topic(id=2, name="Augmented & Virtual Reality"),
        Topic(id=3, name="Cryptocurrency"),
        Topic(id=4, name="Gaming"),
        Topic(id=5, name="Internet of Things"),
        Topic(id=6, name="Technology"),
        Topic(id=7, name="Web Dev"),
    ]

    subreddits = [
        Subreddit(url="ArtificialInteligence", topics=[topics[0]]),
        Subreddit(url="virtualreality", topics=[topics[1]]),
        Subreddit(url="CryptoCurrency", topics=[topics[2]]),
        Subreddit(url="gaming", topics=[topics[3]]),
        Subreddit(url="IOT", topics=[topics[4]]),
        Subreddit(url="technology", topics=[topics[5]]),
        Subreddit(url="webdev", topics=[topics[6]]),
    ]

    db.session.add_all(topics + subreddits)
    db.session.commit()

    print("✅ Database seeded correctly")

