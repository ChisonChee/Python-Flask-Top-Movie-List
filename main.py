from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


MOVIE_API = "YOUR_themoviedb_API"
SEARCH_URL = "https://api.themoviedb.org/3/search/movie?"

# Flask-SQLAlchemy setup: #
# TODO 1: create SQLAlchemy extension.
db = SQLAlchemy()
# TODO 2: create the app.
app = Flask(__name__)
# TODO 3: configure the SQLite database, relative to the app instance folder.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies_list.db"
# TODO 4: initialize the app with the extension.
db.init_app(app)


# Flask-SQLAlchemy define the Columns datas.
# TODO 5: create the class to db model.
class MovieBank(db.Model):
    # TODO 6: declare Columns.
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img = db.Column(db.String(250), nullable=True)


# TODO 7: create the table.
with app.app_context():
    db.create_all()

# FLASK-BOOTSTRAP SETUP
# app = Flask(__name__) <---- must create before proceeding with configuration.
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# add a piece of data to the database by coding.
# with app.app_context():
#     movie = MovieBank(title="Phone Booth",
#                       year="2002",
#                       description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an"
#                                   "extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's"
#                                   "negotiation with the caller leads to a jaw-dropping climax.",
#                       rating=7.3,
#                       ranking=10,
#                       review="My favourite character was the caller.",
#                       img="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#     db.session.add(movie)
#     db.session.commit()


# FlaskForm setup
# TODO 1: Create a class of form.
class editForm(FlaskForm):
    rating = StringField('Your rating out of 10. eg. 9.5/10', validators=[DataRequired()])
    review = StringField('Your new review.', validators=[DataRequired()])
    submit = SubmitField('Done')


class addForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/")
def home():
    # Read Data.
    data = db.session.query(MovieBank).order_by(MovieBank.rating.desc())
    i = 1
    for item in data:
        item.ranking = i
        db.session.commit()
        i += 1
    return render_template("index.html", data=data)


@app.route("/edit?id=<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    data = db.session.execute(db.select(MovieBank).filter_by(id=item_id)).scalar_one()
    edit_form = editForm()
    if request.method == "POST":
        data.rating = request.form['rating']
        data.review = request.form['review']
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("edit.html", data=data, form=edit_form)


@app.route("/add", methods=["GET", "POST"])
def add():
    data = []
    add_form = addForm()
    if request.method == "POST":
        params = {
            "api_key": MOVIE_API,
            "query": request.form['title']
            }
        query = requests.get(SEARCH_URL, params=params).json()
        for item in query['results']:
            the_item = [item['id'], item['title'], item['release_date']]
            data.append(the_item)
        return render_template("select.html", search_list=data)
    else:
        return render_template("add.html", form=add_form)


@app.route("/select?movie_id=<int:movie_id>")
def select(movie_id):
    movie_api = f"https://api.themoviedb.org/3/movie/{movie_id}?"
    params = {
        "api_key": MOVIE_API,
    }
    query = requests.get(movie_api, params=params).json()
    movie = MovieBank(
                      title=query['title'],
                      img=f"https://image.tmdb.org/t/p/original{query['poster_path']}",
                      year=query['release_date'].split("-")[0],
                      description=query['overview'],
                      )
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for("edit", item_id=movie.id))


@app.route("/delete?id=<int:item_id>")
def delete(item_id):
    data = db.session.execute(db.select(MovieBank).filter_by(id=item_id)).scalar_one()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
