import scrape_mars
from flask import Flask

app = Flask(__name__)


# @app.route("/")
# def home():
#     return


@app.route("/scrape")
def scrape():
    content = scrape_mars.scrape()
    return f"<img src={content['hemispheres'][3]['url']}>"


if __name__ == "__main__":
    app.run(debug=True)