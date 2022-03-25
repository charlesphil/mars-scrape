import scrape_mars
from flask import Flask, render_template, redirect, flash
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
# SECRET KEY FOR HOMEWORK PURPOSES ONLY (to enable flash messages)
app.secret_key = "12345"

# Set up mongo connection
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# Connect to mongo db and collection
db = client.mars_db
collection = db.scraped_data


@app.route("/")
def home():
    content = collection.find_one()
    if content is None:
        flash("No content was found. Attempting to scrape new data.", "warning")
        return redirect("/scrape", code=302)
    else:
        try:
            return render_template(
                "index.html",
                latest=content["latest_news"],
                facts_table=content["facts"],
                featured=content["featured_img"],
                hemispheres=content["hemispheres"],
                last_updated=f"Last Updated: {content['last_updated']}"
            )
        except KeyError:
            flash("Incomplete content. Attempting to scrape new data.", "warning")
            return redirect("/scrape", code=302)


@app.route("/scrape")
def scrape():
    updated_data = scrape_mars.scrape()
    try:
        collection.update_one({}, {"$set": updated_data}, upsert=True)
    except ServerSelectionTimeoutError:
        flash("Connection to the database timed out. Check the database URI "
              "or if the service is turned on.", "danger")
        return redirect("/error", code=302)
    else:
        flash("Database successfully refreshed. Content loaded.", "success")
        return redirect("/", code=302)


@app.route("/update")
def update():
    last_date = collection.find_one()['last_updated']
    if last_date is None:
        flash("Date last updated was missing. Attempting to scrape new data.", "warning")
        return redirect("/scrape", code=302)
    else:
        return render_template(
            "update.html",
            last_updated=f"Last Updated: {last_date}"
        )


@app.route("/updating")
def updating():
    return redirect("/scrape", code=302)


@app.route("/about")
def about():
    last_date = collection.find_one()['last_updated']
    if last_date is None:
        flash("Date last updated was missing. Attempting to scrape new data.", "warning")
        return redirect("/scrape", code=302)
    else:
        return render_template(
            "about.html",
            last_updated=f"Last Updated: {last_date}"
        )


@app.route("/error")
def error():
    return render_template("error.html", last_updated="")


if __name__ == "__main__":
    app.run(debug=True)
