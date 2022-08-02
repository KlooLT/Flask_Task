"""
Uzduotys:
1.(3) Surasti, isvardinti ir pataisyti visas projekte rastas klaidas zemiau, uz bent 5 rastas ir pataisytas
pilnas balas:
    a) data = MyTable.query turi buti data = MyTable.query.all()
    b) @app.route('/sign_in'), truksta methods, turi buti @app.route('/sign_in', methods=['GET', 'POST'])
    c) if request.method == 'POST': , turi buti metodas "GET"
    d) form.first_name.data = current_user.email_address , turi bŪti form.first_name.data = current_user.first_name
    e) form.last_name.data = current_user.email_address, turi buti form.last_name.data = current_user.last_name
    f) truksta logout_user(), taip pat reikia ji importuoti
    g) truksta last_name formos registruojantis, reikia pridėti į forms,templates ir main
    h)  first_name = db.Column(db.Integer) pakeista į String
    ...
2.(7) Praplesti aplikacija i bibliotekos registra pagal apacioje surasytus reikalavimus:
    a)(1) Naudojant SQLAlchemy klases, aprasyti lenteles BookReg, Author su pasirinktinais atributais su tinkamu rysiu -
        vienas autorius, gali buti parases daug knygu, ir uzregistruoti juos admin'e
    b)(2) Sukurti (papildomus) reikiamus rysius tarp duombaziniu lenteliu, kad atitiktu zemiau pateiktus reikalavimus
    c) Sukurti puslapius Available Books ir My Books:
        i)(2) Available Books puslapis
            - isvesti bent knygos pavadinima ir autoriu
            - turi buti prieinamas tik vartotojui prisijungus,
            - rodyti visas knygas, kurios nera pasiskolintos
            - tureti mygtuka ar nuoroda "Borrow" prie kiekvienos knygos, kuri/ia paspaudus, knyga yra priskiriama
              varototojui ir puslapis perkraunamas
              (del paprastumo, sakome kad kiekvienos i sistema suvestos knygos turima lygiai 1)
        ii)(2) My Books puslapis
            - turi matytis ir buti prieinamas tik vartotojui prisijungus
            - rodyti visas knygas, kurios yra pasiskolintos prisijungusio vartotojo
            - salia kiekvienos knygos mygtuka/nuoroda "Return", kuri/ia paspaudus, knyga grazinama i biblioteka ir
              perkraunamas puslapis
    f)(2) Bonus: praplesti aplikacija taip, kad bibliotekoje kiekvienos knygos galetu buti
        daugiau negu vienas egzempliorius
Pastabos:
    - uzstrigus su pirmaja uzduotimi, galima paimti musu paskutini flask projekto template
        ir ten atlikti antra uzduoti
    - nereikalingus templates geriau panaikinti ar persidaryti, kaip reikia. Tas pats galioja su MyTable klase
    - antram vartotojui prisijungus, nebeturi matytis kyngos, kurios buvo pasiskolintos pirmojo vartotojo
        nei prie Available Books, nei prie My Books
    - visam administravimui, pvz. knygu suvedidimui galima naudoti admin
    - sprendziant bonus uzduoti, apsvarstyti papildomos lenteles isivedima
"""

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, AnonymousUserMixin, LoginManager, login_user, logout_user, current_user, \
    login_required
from flask_sqlalchemy import SQLAlchemy
import forms

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = False


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)

table1 = db.Table('helper', db.metadata,
                  db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                  db.Column('author_id', db.Integer, db.ForeignKey('author.id')))

table2 = db.Table('helper_2', db.metadata,
                  db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    books = db.relationship('BookReg', secondary=table2)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    books = db.relationship('BookReg', secondary=table1, overlaps="books")
    author = db.relationship('Author', secondary=table1, overlaps="books")


class BookReg(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    stock = db.Column(db.Integer, nullable=False, default=1)


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Author, db.session))
admin.add_view(MyModelView(BookReg, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/my_books')
@login_required
def my_books():
    my_books = BookReg.query.all()
    return render_template('my_books.html', my_books=my_books)


@app.route('/available_books')
@login_required
def available_books():
    avl_books = BookReg.query.all()
    return render_template('available_books.html', avl_books=avl_books)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User e-mail or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


# @app.route("/borrow/<int:id>")
# @login_required
# def borrow(id):
# nespėju aprašyti mygtukų...

@app.route('/update_account_information', methods=['GET', 'POST'])
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form_in_html=form)


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
