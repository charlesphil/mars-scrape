import scrape_mars
from flask import Flask
import pymongo

app = Flask(__name__)

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.scraped_data


# @app.route("/")
# def home():
#     return


@app.route("/scrape")
def scrape():
    content = scrape_mars.scrape()

    return (
        f"<p>{content['latest_news']['title']}</p>"
        f"<p>{content['latest_news']['paragraph']}</p>"
        f"<a href={content['latest_news']['url']}>Article Link</a>"
        f"<p>{content['featured_img']['name']}</p>"
        f"<img src={content['featured_img']['img_url']}>"
        f"<a href={content['featured_img']['article_url']}>Article Link</a>"
        f"{content['facts']}"
        f"<p>{content['hemispheres'][0]['name']}</p>"
        f"<img src={content['hemispheres'][0]['url']}>"
        f"<p>{content['hemispheres'][1]['name']}</p>"
        f"<img src={content['hemispheres'][1]['url']}>"
        f"<p>{content['hemispheres'][2]['name']}</p>"
        f"<img src={content['hemispheres'][2]['url']}>"
        f"<p>{content['hemispheres'][3]['name']}</p>"
        f"<img src={content['hemispheres'][3]['url']}>"
    )


if __name__ == "__main__":
    app.run(debug=True)