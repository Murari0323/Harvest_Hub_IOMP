"""
HarvestHub — Main Flask Application
=====================================
Entry-point for the HarvestHub web application.
Run with:  python app.py
"""

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash)
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# ML modules
from ml.recommender import recommend_crop
from ml.price_predictor import get_crop_names, predict_price, load_models

# ── App & Config ────────────────────────────────────────────────
app = Flask(__name__)

# Load config from config.py
from config import Config
app.config['SECRET_KEY'] = Config.SECRET_KEY

# ── Database Connection Pool (SSL-enabled for Aiven) ────────────
db_config = {
    'host':     Config.MYSQL_HOST,
    'port':     Config.MYSQL_PORT,
    'user':     Config.MYSQL_USER,
    'password': Config.MYSQL_PASSWORD,
    'database': Config.MYSQL_DB,
}

# Enable SSL only when not connecting to localhost (i.e. Aiven / remote)
if Config.MYSQL_HOST not in ('localhost', '127.0.0.1'):
    db_config['ssl_disabled'] = False
    db_config['ssl_verify_cert'] = False

# Create a connection pool for better reliability
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="harvesthub_pool",
        pool_size=5,
        pool_reset_session=True,
        **db_config
    )
except mysql.connector.Error as e:
    print(f"[WARNING] Could not create connection pool at startup: {e}")
    connection_pool = None


def get_db():
    """Get a database connection from the pool (or create a fresh one)."""
    try:
        if connection_pool:
            return connection_pool.get_connection()
    except mysql.connector.Error:
        pass
    # Fallback: create a standalone connection
    return mysql.connector.connect(**db_config)


# Pre-load ML models at startup
with app.app_context():
    load_models()


# ================================================================
# HELPER DECORATORS
# ================================================================

def login_required(f):
    """Redirect to login page if user is not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_required(role):
    """Restrict access to users with a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ================================================================
# 1.  LANDING PAGE
# ================================================================

@app.route('/')
def index():
    """Landing / home page."""
    return render_template('index.html')


# ================================================================
# 2.  AUTHENTICATION MODULE
# ================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new farmer or buyer account."""
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        role     = request.form['role']       # 'farmer' or 'buyer'
        location = request.form.get('location', '')

        # Hash password
        hashed_pw = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password, role, location) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_pw, role, location)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            if 'Duplicate' in str(e) or '1062' in str(e):
                flash('Email already registered.', 'danger')
            else:
                flash(f'Registration failed: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and create session."""
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['user_id']
            session['name']     = user['name']
            session['email']    = user['email']
            session['role']     = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')

            # Redirect to the appropriate dashboard
            if user['role'] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            else:
                return redirect(url_for('marketplace'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear session and log out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ================================================================
# 3.  FARMER MANAGEMENT MODULE
# ================================================================

@app.route('/farmer/dashboard')
@login_required
@role_required('farmer')
def farmer_dashboard():
    """Show the farmer's own crop listings and received orders."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Farmer's crops
    cur.execute("SELECT * FROM crops WHERE farmer_id = %s ORDER BY created_at DESC",
                (session['user_id'],))
    crops = cur.fetchall()

    # Orders received for this farmer's crops
    cur.execute("""
        SELECT o.*, c.crop_name, u.name AS buyer_name
        FROM orders o
        JOIN crops c ON o.crop_id = c.crop_id
        JOIN users u ON o.buyer_id = u.user_id
        WHERE o.farmer_id = %s
        ORDER BY o.order_date DESC
    """, (session['user_id'],))
    orders = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('farmer_dashboard.html', crops=crops, orders=orders)


@app.route('/farmer/add_crop', methods=['GET', 'POST'])
@login_required
@role_required('farmer')
def add_crop():
    """Add a new crop listing."""
    if request.method == 'POST':
        crop_name   = request.form['crop_name']
        quantity    = request.form['quantity']
        price       = request.form['price']
        category    = request.form.get('category', 'General')
        season      = request.form.get('season', '')
        description = request.form.get('description', '')
        image_url   = request.form.get('image_url', '')

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crops (farmer_id, crop_name, quantity, price, "
            "category, season, description, image_url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (session['user_id'], crop_name, quantity, price,
             category, season, description, image_url)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Crop added successfully!', 'success')
        return redirect(url_for('farmer_dashboard'))

    return render_template('add_crop.html')


@app.route('/farmer/edit_crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
@role_required('farmer')
def edit_crop(crop_id):
    """Edit an existing crop listing (only if owned by logged-in farmer)."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cur.execute(
            "UPDATE crops SET crop_name=%s, quantity=%s, price=%s, "
            "category=%s, season=%s, description=%s, image_url=%s, status=%s "
            "WHERE crop_id=%s AND farmer_id=%s",
            (request.form['crop_name'], request.form['quantity'],
             request.form['price'], request.form.get('category', 'General'),
             request.form.get('season', ''), request.form.get('description', ''),
             request.form.get('image_url', ''), request.form.get('status', 'available'),
             crop_id, session['user_id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Crop updated!', 'success')
        return redirect(url_for('farmer_dashboard'))

    cur.execute("SELECT * FROM crops WHERE crop_id = %s AND farmer_id = %s",
                (crop_id, session['user_id']))
    crop = cur.fetchone()
    cur.close()
    conn.close()

    if not crop:
        flash('Crop not found.', 'danger')
        return redirect(url_for('farmer_dashboard'))

    return render_template('edit_crop.html', crop=crop)


@app.route('/farmer/delete_crop/<int:crop_id>', methods=['POST'])
@login_required
@role_required('farmer')
def delete_crop(crop_id):
    """Delete a crop listing."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM crops WHERE crop_id = %s AND farmer_id = %s",
                (crop_id, session['user_id']))
    conn.commit()
    cur.close()
    conn.close()
    flash('Crop deleted.', 'info')
    return redirect(url_for('farmer_dashboard'))


@app.route('/farmer/orders')
@login_required
@role_required('farmer')
def farmer_orders():
    """View orders received by the farmer."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT o.*, c.crop_name, u.name AS buyer_name
        FROM orders o
        JOIN crops c ON o.crop_id = c.crop_id
        JOIN users u ON o.buyer_id = u.user_id
        WHERE o.farmer_id = %s
        ORDER BY o.order_date DESC
    """, (session['user_id'],))
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('orders.html', orders=orders, role='farmer')


@app.route('/farmer/update_order/<int:order_id>', methods=['POST'])
@login_required
@role_required('farmer')
def update_order_status(order_id):
    """Farmer updates order status (confirm, ship, deliver, cancel)."""
    new_status = request.form['status']
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        # Update the order status
        cur.execute(
            "UPDATE orders SET order_status = %s "
            "WHERE order_id = %s AND farmer_id = %s",
            (new_status, order_id, session['user_id'])
        )

        # If delivered, reduce crop quantity
        if new_status == 'delivered':
            # Fetch order details
            cur.execute(
                "SELECT crop_id, quantity FROM orders "
                "WHERE order_id = %s AND farmer_id = %s",
                (order_id, session['user_id'])
            )
            order = cur.fetchone()

            if order:
                # Subtract order qty from crop, ensure >= 0
                cur.execute(
                    "UPDATE crops SET quantity = GREATEST(quantity - %s, 0) "
                    "WHERE crop_id = %s",
                    (order['quantity'], order['crop_id'])
                )
                # If quantity is now 0, mark as sold out
                cur.execute(
                    "UPDATE crops SET status = 'sold_out' "
                    "WHERE crop_id = %s AND quantity <= 0",
                    (order['crop_id'],)
                )

        conn.commit()
        flash(f'Order #{order_id} marked as {new_status}.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to update order: {e}', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('farmer_orders'))


# ================================================================
# 4.  PRODUCT / MARKETPLACE MODULE
# ================================================================

@app.route('/marketplace')
def marketplace():
    """Browse all available crops. Supports search via query param ?q=..."""
    search = request.args.get('q', '').strip()
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if search:
        cur.execute("""
            SELECT c.*, u.name AS farmer_name, u.location AS farmer_location
            FROM crops c JOIN users u ON c.farmer_id = u.user_id
            WHERE c.status = 'available'
              AND (c.crop_name LIKE %s OR c.category LIKE %s)
            ORDER BY c.created_at DESC
        """, (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT c.*, u.name AS farmer_name, u.location AS farmer_location
            FROM crops c JOIN users u ON c.farmer_id = u.user_id
            WHERE c.status = 'available'
            ORDER BY c.created_at DESC
        """)

    crops = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('marketplace.html', crops=crops, search=search)


@app.route('/crop/<int:crop_id>')
def crop_detail(crop_id):
    """View full details of a single crop listing."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.*, u.name AS farmer_name, u.location AS farmer_location
        FROM crops c JOIN users u ON c.farmer_id = u.user_id
        WHERE c.crop_id = %s
    """, (crop_id,))
    crop = cur.fetchone()
    cur.close()
    conn.close()

    if not crop:
        flash('Crop not found.', 'danger')
        return redirect(url_for('marketplace'))

    return render_template('crop_detail.html', crop=crop)


# ================================================================
# 5.  CART & ORDER MODULE
# ================================================================

@app.route('/cart/add/<int:crop_id>', methods=['POST'])
@login_required
@role_required('buyer')
def add_to_cart(crop_id):
    """Add a crop to the session-based shopping cart."""
    qty = float(request.form.get('quantity', 1))

    cart = session.get('cart', {})
    crop_key = str(crop_id)

    if crop_key in cart:
        cart[crop_key]['quantity'] += qty
    else:
        # Fetch crop details
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM crops WHERE crop_id = %s", (crop_id,))
        crop = cur.fetchone()
        cur.close()
        conn.close()

        if not crop:
            flash('Crop not found.', 'danger')
            return redirect(url_for('marketplace'))

        cart[crop_key] = {
            'crop_id':   crop['crop_id'],
            'crop_name': crop['crop_name'],
            'price':     float(crop['price']),
            'quantity':  qty,
            'farmer_id': crop['farmer_id'],
        }

    session['cart'] = cart
    flash('Added to cart!', 'success')
    return redirect(url_for('marketplace'))


@app.route('/cart')
@login_required
@role_required('buyer')
def view_cart():
    """View shopping cart."""
    cart = session.get('cart', {})
    items = list(cart.values())
    total = sum(i['price'] * i['quantity'] for i in items)
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/remove/<int:crop_id>', methods=['POST'])
@login_required
@role_required('buyer')
def remove_from_cart(crop_id):
    """Remove an item from the cart."""
    cart = session.get('cart', {})
    cart.pop(str(crop_id), None)
    session['cart'] = cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))


@app.route('/order/place', methods=['POST'])
@login_required
@role_required('buyer')
def place_order():
    """Convert cart items into orders."""
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('view_cart'))

    conn = get_db()
    cur = conn.cursor()
    try:
        for item in cart.values():
            total = item['price'] * item['quantity']
            cur.execute(
                "INSERT INTO orders (buyer_id, crop_id, farmer_id, "
                "quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
                (session['user_id'], item['crop_id'],
                 item['farmer_id'], item['quantity'], total)
            )
        conn.commit()
        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Order failed: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('buyer_orders'))


@app.route('/orders')
@login_required
@role_required('buyer')
def buyer_orders():
    """View buyer's order history."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT o.*, c.crop_name, u.name AS farmer_name
        FROM orders o
        JOIN crops c ON o.crop_id = c.crop_id
        JOIN users u ON o.farmer_id = u.user_id
        WHERE o.buyer_id = %s
        ORDER BY o.order_date DESC
    """, (session['user_id'],))
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('orders.html', orders=orders, role='buyer')


# ================================================================
# 6.  CROP RECOMMENDATION MODULE
# ================================================================

@app.route('/recommend', methods=['GET', 'POST'])
@login_required
def crop_recommendation():
    """AI-powered rule-based crop recommendation."""
    result = None
    if request.method == 'POST':
        soil        = request.form['soil_type']
        temperature = float(request.form['temperature'])
        rainfall    = float(request.form['rainfall'])
        season      = request.form['season']

        result = recommend_crop(soil, temperature, rainfall, season)

        # Log to database
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recommendations "
            "(soil_type, temperature, rainfall, season, recommended_crop) "
            "VALUES (%s, %s, %s, %s, %s)",
            (soil, temperature, rainfall, season, result['crop'])
        )
        conn.commit()
        cur.close()
        conn.close()

    return render_template('recommend.html', result=result)


# ================================================================
# 7.  PRICE PREDICTION MODULE
# ================================================================

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def price_prediction():
    """Predict future crop price using Linear Regression."""
    crops = get_crop_names()
    prediction = None

    if request.method == 'POST':
        crop_name = request.form['crop_name']
        year      = int(request.form['year'])
        month     = int(request.form['month'])

        predicted = predict_price(crop_name, year, month)
        prediction = {
            'crop':  crop_name,
            'year':  year,
            'month': month,
            'price': predicted,
        }

        # Log to database
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (crop_name, predicted_price, prediction_date) "
            "VALUES (%s, %s, %s)",
            (crop_name, predicted, f'{year}-{month:02d}-01')
        )
        conn.commit()
        cur.close()
        conn.close()

    return render_template('predict.html', crops=crops, prediction=prediction)


# ================================================================
# RUN
# ================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
