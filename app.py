from email.mime import image
import select

from flask import Flask, app, jsonify, request, flash, redirect, session, url_for, render_template
import sqlite3,json
app = Flask(__name__)
app.secret_key = 'your_secret_key'
def load_data():
    with open('shopping-data/type.json') as f:
        donut_temp = json.load(f)
    with open('shopping-data/topping.json') as f:
        toppings = json.load(f)
    with open('shopping-data/sprinkle.json') as f:
        sprinkles = json.load(f)
    return donut_temp, toppings, sprinkles
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
def generate_user_list():
    conn = sqlite3.connect('databaseuser.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,

              email TEXT,
              password TEXT)''')
    conn.commit()
    conn.close(    )
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('databaseuser.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.')
        return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    username=session.get('user')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('databaseuser.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            flash('Login successful!')
            session['user'] = user[1]  # Store the user's name in the session
            print(f"User {user[1]} logged in successfully.")
            return redirect(url_for('index'))
            
        else:
            flash('Invalid email or password.')
            return redirect(url_for('index'))
@app.route('/user')
def user():
    return render_template('login.html')
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

        conn = sqlite3.connect('databaseuser.db')
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
    session['user'] = session.get('user', None)
    print(f"Current user in session: {session['user']}")
    donut_temp, toppings, sprinkles = load_data()
    price_display = {donut: details['price'] for donut, details in donut_temp.items()}
    return render_template('menu.html', donut_temp=donut_temp, toppings=toppings, sprinkles=sprinkles, price_display=price_display)
@app.route('/remove_from_cart')
def remove_from_cart():
    item_info = request.args.get('item_info')
    cart = session.get('cart', {})
    if item_info in cart:
        del cart[item_info]
        session['cart'] = cart
        session.modified = True
        flash(f'Item {item_info} removed from cart.')
    else:
        flash(f'Item {item_info} not found in cart.')
             
    return redirect(url_for('add_to_cart'))

@app.route('/checkout', methods=['POST', 'GET'])
def add_to_cart():
    try:
        main_order = request.form['main_order']
        toppings = request.form['topping']
        sprinkles = request.form['sprinkle']
        quantity = int(request.form['quantity'])
        donut_temp, toppings_data, sprinkles_data = load_data()
        cart = session.get('cart', {})
        if sprinkles in sprinkles_data:
            selected_sprinkles = sprinkles_data[sprinkles]
            sprinkles_price = float(selected_sprinkles['price'])
            print(f"Selected sprinkles: {selected_sprinkles}, Price: {sprinkles_price}")
        else:
            selected_sprinkles = None
            sprinkles_price = 0.0
            print("No sprinkles selected or invalid selection.")
        if toppings in toppings_data:
            selected_toppings = toppings_data[toppings]
            toppings_price = float(selected_toppings['price'])
            print(f"Selected toppings: {selected_toppings}, Price: {toppings_price}")
        else:
            selected_toppings = None
            toppings_price = 0.0
            print("No toppings selected or invalid selection.")
        item_info=f"{main_order}|{toppings}|{sprinkles}"
        #determining the exact combination of items if it was already in cart or not
        total_price = (float(donut_temp[main_order]['price']) + toppings_price + sprinkles_price) * quantity
        flash(f'Added {quantity} {main_order}(s) to cart with toppings: {toppings} and sprinkles: {sprinkles}. Total price: ${total_price:.2f}')
            
        if item_info in cart:

            cart[item_info]['quantity'] += quantity
            cart[item_info]['total_price'] += total_price
        else:
            cart[item_info] = {

                'quantity': quantity, 
                'total_price': total_price}
        print(f"Item info: {item_info}")
        print(f"Cart contents: {cart}")
        session['cart']=cart
        session.modified = True
        return render_template('checkout.html', main_order=main_order, toppings=toppings, sprinkles=selected_sprinkles, cart=cart, total_price=total_price, quantity=quantity)

    except Exception as e:
        cart = session.get('cart', {})

    
        session['cart']=cart
        session.modified = True
        return render_template('checkout.html', cart=cart)
   
@app.route('/payup', methods=['POST'])
def payup():
    user = session.get('user', None)
    cart = session.get('cart', {})
    total_price = sum(item['total_price'] for item in cart.values())
    return render_template('payment.html', cart=cart, total_price=total_price, user=user)
    


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
    price=request.form['price']
    return render_template('verify-order.html',price=price, main_order=main_order, toppings=topping_data, sprinkles=sprinkle_data, image=image)
if __name__ == '__main__':
    create_db()
    generate_user_list()
    app.run(debug=True)