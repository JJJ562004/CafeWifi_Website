from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, SelectField, RadioField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=True)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=True)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=True)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name:', validators=[DataRequired()])
    map = URLField('Map URL: ', validators=[DataRequired(), URL()])
    location = StringField('Location:', validators=[DataRequired()])
    image = URLField('Image URL:', validators=[DataRequired(), URL()])
    has_sockets = RadioField('Does it have sockets?',
                             choices=[('yes', 'Of course!'), ('no', 'Sadly no..')],
                             validators=[DataRequired()])
    has_toilet = RadioField('Does it have toilet?',
                            choices=[('yes', 'Of course!'), ('no', 'Sadly no..')],
                            validators=[DataRequired()])
    has_wifi = RadioField('Does it have wifi?',
                          choices=[('yes', 'Of course!'), ('no', 'Sadly no..')],
                          validators=[DataRequired()])
    can_take_calls = RadioField('Can i take calls?',
                                choices=[('yes', 'Of course!'), ('no', 'Sadly no..')],
                                validators=[DataRequired()])
    seats = SelectField('How many seats are there?',
                        choices=[('0-10', '0-10'), ('10 -20', '10-20'), ('20-30', '20-30'), ('30-40', '30-40'),
                                 ('50+', '50+')],
                        validators=[DataRequired()])
    coffee_price = StringField("The price: eg. $30.2", validators=[DataRequired()])
    submit = SubmitField('Submit')


# ---------------------------------------------------------------------------

def getattr_filter(obj, attr):
    return getattr(obj, attr)


app.jinja_env.filters['getattr'] = getattr_filter


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        if form.has_sockets.data == 'yes':
            has_sockets = True
        else:
            has_sockets = False
        if form.has_wifi.data == 'yes':
            has_wifi = True
        else:
            has_wifi = False
        if form.has_toilet.data == 'yes':
            has_toilet = True
        else:
            has_toilet = False
        if form.can_take_calls.data == 'yes':
            can_take_calls = True
        else:
            can_take_calls = False
        c = Cafe(
            name=form.cafe.data,
            img_url=form.image.data,
            map_url=form.map.data,
            location=form.location.data,
            has_sockets=has_sockets,
            has_wifi=has_wifi,
            has_toilet=has_toilet,
            can_take_calls=can_take_calls,
            seats=form.seats.data,
            coffee_price=form.can_take_calls.data
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    all_cafes = Cafe.query.all()
    print(all_cafes)
    return render_template('cafes.html', cafes=all_cafes)

@app.route('/edit', methods =['GET', 'POST'])
def edit_cafe():
    cafe_id = request.args.get('id')
    cafe = db.get_or_404(Cafe, cafe_id)

    form = CafeForm(obj=cafe)
    if form.validate_on_submit():
        form.populate_obj(cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template("add.html", form=form)

@app.route("/delete")
def delete_cafe():
    cafe_id = request.args.get('id')
    cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for("cafes"))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
