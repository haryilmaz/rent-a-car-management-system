from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentacar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), unique=True, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    car = db.relationship('Car', backref=db.backref('rentals', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('rentals', lazy=True))

@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        new_car = Car(
            plate=request.form['plate'],
            brand=request.form['brand'],
            model=request.form['model'],
            year=request.form['year'],
            daily_rate=request.form['daily_rate'],
            is_available=True
        )
        db.session.add(new_car)
        db.session.commit()
        flash('Araç başarıyla eklendi!', 'success')
        return redirect(url_for('index'))
    return render_template('add_car.html')

@app.route('/rent_car/<int:car_id>', methods=['GET', 'POST'])
def rent_car(car_id):
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        new_customer = Customer(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone']
        )
        db.session.add(new_customer)
        db.session.commit()

        new_rental = Rental(
            car_id=car.id,
            customer_id=new_customer.id,
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            total_price=car.daily_rate * (int(request.form['end_date']) - int(request.form['start_date']))
        )
        db.session.add(new_rental)
        car.is_available = False
        db.session.commit()
        flash('Araç kiralama işlemi başarılı!', 'success')
        return redirect(url_for('index'))
    return render_template('rent_car.html', car=car)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
