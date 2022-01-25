# •	The first line says that we'll use Flask to render a template, redirecting to another url, and creating a URL.
# •	The second line says we'll use PyMongo to interact with our Mongo database.
# •	The third line says that to use the scraping code, we will convert from Jupyter notebook to Python.

from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import scraping
app = Flask(__name__)
# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)
@app.route("/")
def index():
    # uses PyMongo to find the "mars" collection in our database, which we will create when we convert our 
    # Jupyter scraping code to Python Script. We will also assign that path to the mars variable for use later.
   mars = mongo.db.mars.find_one()
   return render_template("index.html", mars=mars)

# defines the route that Flask will be using. This route, “/scrape”, will run the function that 
# we create just beneath it.
# The next lines allow us to access the database, scrape new data using our scraping.py script, 
# update the database, and return a message when successful. 

@app.route("/scrape")
def scrape():
    # /we assign a new variable that points to our Mongo database
   mars = mongo.db.mars
#    Next, we created a new variable to hold the newly scraped data: 
   mars_data = scraping.scrape_all()
#    we're referencing the scrape_all function in the scraping.py file exported from Jupyter Notebook
# upsert=True. This indicates to Mongo to create a new document if one doesn't already exist, 
# and new data will always be saved (even if we haven't already created a document for it).
   mars.update_one({}, {"$set":mars_data}, upsert=True)
#    that we've gathered new data, we need to update the database 
# we will add a redirect after successfully scraping the data: return redirect('/', code=302). 
# This will navigate our page back to / where we can see the updated content.
   return redirect('/', code=302)
if __name__ == "__main__":
   app.run()
