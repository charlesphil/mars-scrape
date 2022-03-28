import scrape_mars
from flask import Flask, render_template, redirect, flash, request
from werkzeug.user_agent import UserAgent
from ua_parser import user_agent_parser
from werkzeug.utils import cached_property
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
# SECRET KEY FOR HOMEWORK PURPOSES ONLY (to enable flash messages)
app.secret_key = "12345"

# Set up mongo connection (LOCALHOST FOR HOMEWORK PURPOSES ONLY)
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# Connect to database and collection
db = client.mars_db
collection = db.scraped_data


# Class that parses UserAgent string and defines browser
# property from parsed string
class ParsedUserAgent(UserAgent):
    @cached_property
    def _details(self):
        return user_agent_parser.Parse(self.string)

    @property
    def browser(self):
        return self._details["user_agent"]["family"]


# Function to check browser compatibility
def is_compatible():
    # create new ParsedUserAgent object
    user_agent = ParsedUserAgent(request.headers.get("User-Agent"))

    # If the browser is not either Chrome or Firefox, create a new flash message
    # and return False, otherwise return True
    if user_agent.browser != "Chrome" and user_agent.browser != "Firefox":
        flash(
            (f"This browser ({user_agent.browser}) "
             f"is not compatible with this site. Please use either "
             f"<a href='https://www.google.com/chrome/downloads/'>"
             f"Google Chrome</a> or <a href='https://www.mozilla.org/"
             f"en-US/firefox/new/'>Mozilla Firefox</a>."),
            "danger"
        )
        return False
    else:
        return True


@app.route("/")
def home():
    # Check browser for compatibility
    if not is_compatible():
        return redirect("/error", code=302)

    # If server times out, redirect to error page with flash message
    try:
        content = collection.find_one()
    except ServerSelectionTimeoutError:
        flash("Connection to the database timed out. Check the database URI "
              "or if the database is running.", "danger")
        return redirect("/error", code=302)

    # Check if content is available to pull from database, scrape if empty
    if content is None:
        flash(
            "No content was found. Attempting to scrape new data.",
            "warning"
        )
        return redirect("/scrape", code=302)
    else:
        # Load content from database
        try:
            return render_template(
                "index.html",
                latest=content["latest_news"],
                facts_table=content["facts"],
                featured=content["featured_img"],
                hemispheres=content["hemispheres"],
                last_updated=f"Last Scraped: {content['last_updated']}"
            )
        # If database does not have all the required data, scrape new data
        except KeyError:
            flash(
                "Incomplete content. Attempting to scrape new data.",
                "warning"
            )
            return redirect("/scrape", code=302)


@app.route("/scrape")
def scrape():
    # Run scrape function from imported module
    updated_data = scrape_mars.scrape()

    # Try to update document in database
    try:
        collection.update_one({}, {"$set": updated_data}, upsert=True)
    # If connection times out, redirect to /error if failed, otherwise home
    except ServerSelectionTimeoutError:
        flash("Connection to the database timed out. Check the database URI "
              "or if the database is running.", "danger")
        return redirect("/error", code=302)
    else:
        flash("Database successfully refreshed. Content loaded.", "success")
        return redirect("/", code=302)


@app.route("/update")
def update():
    # Check browser for compatibility
    if not is_compatible():
        return redirect("/error", code=302)

    # Get last updated date from document in database
    try:
        last_date = collection.find_one()['last_updated']
    except ServerSelectionTimeoutError:
        flash("Connection to the database timed out. Check the database URI "
              "or if the database is running.", "danger")
        return redirect("/error", code=302)

    # If empty, scrape new data
    if last_date is None:
        flash(
            "Date last updated was missing. Attempting to scrape new data.",
            "warning"
        )
        return redirect("/scrape", code=302)
    # Otherwise, render the page and load the timestamp into the navigation bar
    else:
        return render_template(
            "update.html",
            last_updated=f"Last Scraped: {last_date}"
        )


@app.route("/about")
def about():
    # Check browser for compatibility
    if not is_compatible():
        return redirect("/error", code=302)

    # Get last updated date from document in database
    try:
        last_date = collection.find_one()['last_updated']
    except ServerSelectionTimeoutError:
        flash("Connection to the database timed out. Check the database URI "
              "or if the database is running.", "danger")
        return redirect("/error", code=302)

    # If empty, scrape new data
    if last_date is None:
        flash(
            "Date last updated was missing. Attempting to scrape new data.",
            "warning"
        )
        return redirect("/scrape", code=302)
    # Otherwise, render the page and load the timestamp into the navigation bar
    else:
        return render_template(
            "about.html",
            last_updated=f"Last Scraped: {last_date}"
        )


@app.route("/error")
def error():
    # Load error page, make timestamp blank
    return render_template("error.html", last_updated="")


if __name__ == "__main__":
    app.run(debug=True)
