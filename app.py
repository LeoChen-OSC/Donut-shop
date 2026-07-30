from email.mime import image
import select

from flask import Flask, app, jsonify, request, flash, redirect, session, url_for, render_template
import sqlite3,json
app = Flask(__name__)
app.secret_key = 'your_secret_key'
def load_data():
    with open('shopping-data/type.json') as f:
        flowers = json.load(f)
    with open('shopping-data/topping.json') as f:
        toppings = json.load(f)
    with open('shopping-data/sprinkle.json') as f:
        sprinkles = json.load(f)
    return flowers, toppings, sprinkles
@app.route('/')
def index():
    return render_template('index.html')
def create_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              name TEXT,
              email TEXT,
              orders TEXT,
              phonenum TEXT,
              password TEXT)''')
    conn.commit()
    conn.close()
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    orders = request.form['orders']
    phonenum = request.form['phonenum']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email, orders, phonenum) VALUES (?, ?, ?, ?)", (name, email, orders, phonenum))
    conn.commit()
    conn.close()

    flash('Order loaded!')
    return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])
def login_submit():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('index'))
@app.route('/menu')
def menu():
    return render_template('menu.html')
@app.route('/checkout', methods=['POST'])
def add_to_cart():

    main_order = request.form['main_order']
    toppings = request.form.getlist('toppings')
    sprinkles = request.form.getlist('sprinkles')
    quantity = int(request.form['quantity'])
    main_order1=load_data()
    cart = session.get('cart', {})
    if main_order1 not in main_order1:
        flash('Invalid main order selection.')

    else:
        cart[main_order] = {
            'main-price': 2.00,  # Assuming a fixed price for simplicity
            'topping_price':toppings[toppings]['price'],
            'sprinkle_price':sprinkles[sprinkles]['price'],
            'quantity': quantity
        }
    session['cart'] = cart
    
    session.modified = True
    def calculate_total_one_item():
        main_price =int(2)
        topping_price = int(cart[main_order]['topping_price'])
        sprinkle_price = int(cart[main_order]['sprinkle_price'])
        quantity = int(cart[main_order]['quantity'])
        total_1 = (main_price + topping_price + sprinkle_price) * quantity
        return total_1
    total_2 = calculate_total_one_item()
    flash(f'Item added to cart! {main_order} alongside {toppings} and {sprinkles} with quantity {quantity}, total: ${total_2:.2f}.')
    

    return render_template('checkout.html', main_order=main_order, toppings=toppings, sprinkles=sprinkles)



@app.route('/verify', methods=['POST'])
def verify():
    with open('shopping-data/type.json') as f:
        menu_data = json.load(f)
    with open('shopping-data/topping.json') as f:
        topping_data = json.load(f) 
    with open('shopping-data/sprinkle.json') as f:
        sprinkle_data = json.load(f)
    main_order = request.form['main_order']
    image=request.form['image']

    return render_template('verify-order.html', main_order=main_order, toppings=topping_data, sprinkles=sprinkle_data, image=image)
if __name__ == '__main__':
    create_db()
    app.run(debug=True)