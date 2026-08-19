from email.mime import image
import select,datetime

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
    cartline=0
    session['user'] = session.get('user', None)
    cart=session.get('cart' ,None)
    for item in cart:
        cartline=cartline+cart[item]['quantity']
    print(cartline)
    return render_template('index.html', session=session,cart=cart,cartline=cartline)
def create_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              email TEXT NOT NULL,
              orders TEXT,
              name TEXT,
              address TEXT,
              method TEXT,  
              date TEXT,
              total_price TEXT
              
              )''')
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
        check_user = c.execute("SELECT * FROM users WHERE email=?", (email,))
        if check_user.fetchone():
            flash('Email already registered.')
            return redirect(url_for('index'))
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
@app.route('/search')
def search():
    Search_item=request.args.get('query')
    donut, toppings, sprinkles = load_data()
    search_query="true"
    donut_temp = []
    for donuts in donut:
        if Search_item.lower() in donuts.lower():
            donut_temp.append(donuts)
    return render_template('menu.html', donut_temp=donut_temp, toppings=toppings, sprinkles=sprinkles, search_query=search_query)
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
    #detects if values are entered into the cart data
    try:
        #requests the data from the form and stores it as variables
        main_order = request.form['main_order']
        toppings = request.form['topping']
        sprinkles = request.form['sprinkle']
        #trys to detect invalid number input,otherwise it will redirect back to menu page
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            flash('Invalid quantity. Please enter a valid number.')
            return redirect(url_for('menu'))
        #loads all the menu items in jsons, including toppings and sprinkles.
        donut_temp, toppings_data, sprinkles_data = load_data()
        #loads the cart session, if it does not exist, creates a new cart session
        cart = session.get('cart', {})
        #determine the total price of sprinkle, toppings and determine if the selection is valid
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
        #joins the the combination of main order, topping and sprinkle as one variable, 
        #so it can be used as a key to determine if the combination is already in the cart or not.
        item_info=f"{main_order}|{toppings}|{sprinkles}"
        total_price = (float(donut_temp[main_order]['price']) + toppings_price + sprinkles_price) * quantity
        flash(f'Added {quantity} {main_order}(s) to cart with toppings: {toppings} and sprinkles: {sprinkles}. Total price: ${total_price:.2f}')
        #checks the combination already exists in cart
        if item_info in cart:

            cart[item_info]['quantity'] += quantity
            cart[item_info]['total_price'] += total_price
        else:
            cart[item_info] = {

                'quantity': quantity, 
                'total_price': total_price}
        print(f"Item info: {item_info}")
        print(f"Cart contents: {cart}")
        #exports the cart data into the session, saving it for later use.
        session['cart']=cart
        session.modified = True
        return render_template('checkout.html', main_order=main_order, toppings=toppings, sprinkles=selected_sprinkles, cart=cart, total_price=total_price, quantity=quantity)
    #for a user deleting a item from the cart, or a redirect to the cart page.
    except Exception as e:
        cart = session.get('cart', {})
        total_price=0
        session['cart']=cart
        session.modified = True
        for item in cart:
            total_price=total_price+cart[item]['total_price'] 

        return render_template('checkout.html', cart=cart,total_price=total_price)
   
@app.route('/payup', methods=['POST'])
def payup():
    user = session.get('user', None)
    cart = session.get('cart', {})
    total_price = sum(item['total_price'] for item in cart.values())
    return render_template('payment.html', cart=cart, total_price=total_price, user=user)
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))
@app.route('/cartclear', methods=['POST'])
def cartclear():
    #removes all the session cart data, clearing it.
    session.pop('cart', None)
    flash('Cart cleared!')
    return redirect(url_for('add_to_cart'))
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (order_id,))
        conn.commit()
    flash(f'Order {order_id} deleted!')
    return redirect(url_for('history'))
@app.route('/verify', methods=['POST'])
def verify():
    #loads all the menu items in jsons
    with open('shopping-data/type.json') as f:
        menu_data = json.load(f)
    with open('shopping-data/topping.json') as f:
        topping_data = json.load(f) 
    with open('shopping-data/sprinkle.json') as f:
        sprinkle_data = json.load(f)
    #requests what the user has ordered, then records it down as a variable.
    main_order = request.form['main_order']
    image=request.form['image']
    price=request.form['price']
    return render_template('verify-order.html',price=price, main_order=main_order, 
                           toppings=topping_data, sprinkles=sprinkle_data, image=image)
@app.route('/submit_order', methods=['POST'])
def submit_order():
    user = session.get('user', None)
    print(user)
    if user is None:
        flash('Please log in to submit your order.')
        return redirect(url_for('index'))
    cart = json.dumps(session.get('cart', {}))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_price = request.form['total_price']
    try:
        address = request.form['address']
    except Exception as e:
        address = "No address provided"
        print(f"Error occurred while fetching address: {e}")
    try:
        user_order_name = request.form['name']
    except Exception as e:
        user_order_name = "No name provided"
        print(f"Error occurred while fetching user name: {e}")
    method = request.form['delivery_method']
    print(user)
    #if user is null, they are not logged in the the data is not unecessarily stored in the database.
    if not user=="null" and not user=="None":
        print(f"Submitting order for user: {user}")
        if user=="None":
            flash('Please log in to submit your order.')
            return redirect(url_for('index'))
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email, orders,name,address, method, date, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)", (user, cart, user_order_name, address, method, timestamp, total_price))
        conn.commit()
        conn.close()
        return render_template('index.html', message_disp='Thanks for shopping at donut stoppers!')
    else:
        flash('Please log in to submit your order.')
        return redirect(url_for('index'))
@app.route('/history')
def history():
    user = session.get('user', None)
    print(user)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users ")
    c.execute("SELECT * FROM users WHERE email=?", (user,))
    orders = c.fetchall()
    print(f"Fetched orders for user {user}: {orders}")
    conn.close()
    user_order_list = []
    for order in orders:
        user_order_list.append({
                'order_id': order[0],
                'email': order[1],
                'item_orders': json.loads(order[2]), 
                'name': order[3],
                'address': order[4],
                'method': order[5],
                'total': order[6],
                'date': order[7]

            })
    print(f"Order history for user {user}: {user_order_list}")
    return render_template('history.html', orders=user_order_list, user=user)
if __name__ == '__main__':
    create_db()
    generate_user_list()
    app.run(debug=True)