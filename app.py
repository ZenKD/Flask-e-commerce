from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL
from decimal import Decimal
import bcrypt
import pymysql
app = Flask(__name__)

# MySQL configuration
app.config['SECRET_KEY'] = 'ysecret_key'
app.config['MYSQL_HOST'] = '127.0.0.1'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'password'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'ecom'  # Replace with your database name
app.config['MYSQL_PORT'] = 3306

connection = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB'],
    port=app.config['MYSQL_PORT'])

mysql = MySQL(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        city= request.form['add_city']
        state=request.form['add_state']
        pin=request.form['add_PIN']

        # Check if email already exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer WHERE email = %s", (email,))
        data = cursor.fetchone()
        cursor.close()

        if data:
            flash('Email already exists.', 'danger')
        else:
            # Hash password for security
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert user data into database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO customer (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            connection.commit()
            cursor.close()

            cursor = connection.cursor()
            cursor.execute("SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1;")
            last_customer=cursor.fetchone()
            cursor.close()

            cursor =connection.cursor()
            cursor.execute("INSERT INTO address (customer_id,city,state,zip_code) VALUES (%s,%s,%s,%s)",(last_customer,city,state,pin))
            connection.commit()
            cursor.close()

            flash('Registration successful.', 'success')
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer WHERE email = %s", (email,))
        data = cursor.fetchone()
        cursor.close()

        if data:
            # Check contact_info as password
            if bcrypt.checkpw(password.encode('utf-8'), data[3].encode('utf-8')):
                # Log in user
                flash('Login successful.', 'success')
                session['customer_data']=data
                return redirect(url_for('c_hola'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('login.html')

@app.route('/s_register', methods=['GET', 'POST'])
def s_register():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']

        # Check if contact_info already exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM supplier WHERE contact_info = %s", (contact_info,))
        data = cursor.fetchone()
        cursor.close()

        if data:
            flash('contact_info already exists.', 'danger')
        else:

            # Insert user data into database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO supplier (name, contact_info) VALUES (%s, %s)", (name, contact_info))
            connection.commit()
            cursor.close()

            flash('Registration successful.', 'success')
            return redirect(url_for('index'))

    return render_template('s_register.html')

@app.route('/s_login', methods=['GET', 'POST'])
def s_login():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']

        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM supplier WHERE contact_info = %s", (contact_info,))
        data = cursor.fetchone()
        print(data)
        cursor.close()

        if data:
            # Check password
            if data and data[2]==contact_info:
                # Log in user
                flash('Login successful.', 'success')
                session['supplier_data'] = data    #this actually makes the data store in a flask session which is then accessessd by the s_hola route
                return redirect(url_for('s_hola'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Contact_info not found.', 'danger')

    return render_template('s_login.html')


@app.route('/products')
def products():

    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
        name=customer_data[1]
        email=customer_data[2]

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()  # Fetch all product records
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ordering;")
    ordersl=cursor.fetchall()
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orderitem;")
    orderil=cursor.fetchall()
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("DELETE FROM ordering WHERE order_id NOT IN (SELECT DISTINCT order_id FROM orderitem);")
    connection.commit()
    cursor.close()


    return render_template('products.html',cID=cID,name=name,email=email,products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cart WHERE customer_id = %s", (cID,))
    data = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        product_id = request.form['product_id']
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cartitem (cart_id, product_id, quantity) VALUES (%s, %s, 1)",(data[0], product_id))
        connection.commit()
        cursor.close()

        flash('Product added to cart.', 'success')
    return redirect(url_for('products'))

@app.route('/remove_from_cart',methods=['POST'])
def remove_from_cart():
    if request.method == 'POST':
        cartitem_id = request.form['cart_item_id']
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cartitem WHERE cart_item_id = %s", (cartitem_id,))
        connection.commit()
        cursor.close()

        flash('product removed')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
        name=customer_data[1]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cart WHERE customer_id = %s", (cID,))
    data = cursor.fetchone()
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cartitem WHERE cart_id = %s", (data[0],))
    cart_things = cursor.fetchall()
    cursor.close()


    cursor = connection.cursor()
    cursor.execute("SELECT * FROM product")
    product_thing = cursor.fetchall()
    cursor.close()

    
    
            

    
    return render_template('cart.html',cID=cID,name=name,cart_things=cart_things,product_thing=product_thing)
    
@app.route('/ordering')
def ordering():
    customer_data = session.get('customer_data')
    if customer_data:
        cID = customer_data[0]
        name=customer_data[1]
        email=customer_data[2]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cart WHERE customer_id = %s", (cID,))
    data = cursor.fetchone()
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cartitem WHERE cart_id = %s", (data[0],))
    cart_things = cursor.fetchall()
    cursor.close()


    cursor = connection.cursor()
    cursor.execute("SELECT * FROM product")
    product_thing = cursor.fetchall()
    cursor.close()
    return render_template('ordering.html',cID=cID,name=name,email=email,cart_things=cart_things,product_thing=product_thing)

@app.route('/payment')
def payment():
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
    
    cursor = connection.cursor()
    cursor.execute("SELECT cart_id FROM cart WHERE customer_id = %s", (cID))
    cart_id=cursor.fetchone()
    cursor.close()

    #print(cart_id)
    cursor = connection.cursor()
    cursor.execute("SELECT product_id FROM cartitem WHERE cart_id = %s",(cart_id))
    products1=cursor.fetchall()
    cursor.close()

    a=0.00
    

    for i in products1:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product WHERE product_id = %s",(i))
        vari=cursor.fetchall()
        cursor.close()
        a=a+float(vari[0][3]) 

    cursor = connection.cursor()
    cursor.execute("SELECT wallet FROM customer WHERE customer_id = %s", (cID,))
    wallet = cursor.fetchone()[0]
    cursor.close()  

    if wallet >= Decimal(a):
        # Deduct total price from wallet balance
        new_balance = wallet - Decimal(a)
        cursor = connection.cursor()
        cursor.execute("UPDATE customer SET wallet = %s WHERE customer_id = %s", (new_balance, cID))
        connection.commit()
        cursor.close() 
        cursor = connection.cursor()
        cursor.execute("INSERT INTO ordering (customer_id, total_amount) VALUES (%s, %s)", (cID, a))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ordering ORDER BY order_id DESC LIMIT 1;")
        last_order=cursor.fetchone()
        cursor.close()

        for i in products1:
            cursor = connection.cursor()
            cursor.execute("SELECT price FROM product WHERE product_id = %s",(i))
            price_g=cursor.fetchone()
            cursor.execute("INSERT INTO orderitem (order_id,product_id,price,quantity) VALUES (%s,%s,%s,1)",(last_order[0],i,price_g))
            connection.commit()
            cursor.close()

        for i in products1:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM cartitem WHERE cart_id = %s",(cart_id))
            connection.commit()
            cursor.close()
        
        
        return redirect(url_for('products'))
    else:
        return redirect(url_for('ordering'))



@app.route('/c_hola')
def c_hola():
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
        name=customer_data[1]
        email=customer_data[2]
    

    cursor = connection.cursor()
    cursor.execute("SELECT wallet FROM customer WHERE customer_id = %s", (cID,))
    wallet = cursor.fetchone()
    cursor.close()

    

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cart WHERE customer_id = %s", (cID,))
    data = cursor.fetchone()
    cursor.close()

    if data:
        flash('cart already exists.', 'danger')
    else:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cart (customer_id) VALUES (%s)", (cID))
        connection.commit()
        cursor.close()
        flash('cart created successfully[note this only once per customer]')
    return render_template('c_hola.html',cID=cID,name=name,email=email,wallet=wallet[0])

@app.route('/order')
def show_orders():
    
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
    
    
    cursor=connection.cursor()
    
    cursor.execute("SELECT * FROM ordering WHERE customer_id = %s",(cID))
    orders = cursor.fetchall()
    print(orders)

    cursor.execute("SELECT * FROM product")
    prod=cursor.fetchall()

    
    cursor.execute("SELECT * FROM orderItem")
    order_items = cursor.fetchall()

    # Close the connection
    cursor.close()
    

    return render_template('order.html', orders=orders, order_items=order_items, prod=prod,cID=cID)

@app.route('/s_hola')
def s_hola():
    supplier_data = session.get('supplier_data')
    if supplier_data:
        sID=supplier_data[0]
        name=supplier_data[1]
        contact_info=supplier_data[2]
    return render_template('s_hola.html',sID=sID,name=name,contact_info=contact_info)

@app.route('/s_add_new_prod', methods=['GET', 'POST'])
def s_add_new_prod():
    supplier_data = session.get('supplier_data')
    if supplier_data:
        sID=supplier_data[0]
        name=supplier_data[1]
        contact_info=supplier_data[2]
    if request.method == 'POST':
        product_id = request.form['product_id']
        name1 = request.form['name']
        desc=request.form['desc']
        price=request.form['price']
        stock_quantity=request.form['stock_quantity']
        
        #check if same product_id already present
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
        data = cursor.fetchone()
        cursor.close()

        if data:
            flash('product_id already exists.', 'danger')
        else:
            # Insert product data into database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO product (product_id,name,description,price,stock_quantity) VALUES (%s, %s,%s,%s,%s)", (product_id,name1,desc,price,stock_quantity))
            connection.commit()
            cursor.close()


            #to link the product to the supplier
            cursor =connection.cursor()
            cursor.execute("INSERT INTO productsupplier (product_id,supplier_id) VALUES (%s, %s)", (product_id,sID))
            connection.commit()
            cursor.close()
            
            flash('product creation successful', 'success')
            return redirect(url_for('s_hola'))


    
    return render_template('s_add_new_prod.html')


@app.route('/customer')
def customer():
    return render_template('customer.html')

@app.route('/supplier')
def supplier():
    return render_template('supplier.html')

@app.route('/addwallet')
def addwallet():
    customer_data = session.get('customer_data')
    if customer_data:
        cID=customer_data[0]
    cursor = connection.cursor()
    cursor.execute("UPDATE customer SET wallet = wallet + 100 WHERE customer_id = %s", (cID,))
    connection.commit()
    cursor.close()
    return redirect(url_for('c_hola'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)