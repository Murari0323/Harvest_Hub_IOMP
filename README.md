# 🌾 HarvestHub — Intelligent Online Marketplace for Farmers

**HarvestHub** is a full-stack web application that bridges the gap between farmers and buyers by providing a smart agricultural marketplace with AI-powered crop recommendations and price predictions.

> Built with **Flask**, **MySQL**, and **scikit-learn** for academic demonstration.

---

## ✨ Features

### 🧑‍🌾 Farmer Module
- Register and manage farmer profile
- Add, edit, and delete crop listings
- View and manage incoming orders (confirm, ship, deliver, cancel)

### 🛒 Buyer Module
- Browse the marketplace and search crops
- View detailed crop information
- Add to cart and place orders
- Track order history

### 🤖 AI/ML Modules
- **Crop Recommendation Engine** — Rule-based system that suggests the best crop based on soil type, temperature, rainfall, and season
- **Price Prediction** — Linear Regression model trained on historical data to predict future crop prices

### 🔐 Authentication
- Secure registration and login with hashed passwords
- Role-based access control (Farmer / Buyer)
- Session management

---

## 🛠️ Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python, Flask                     |
| Frontend    | HTML5, CSS3, JavaScript, Jinja2   |
| Database    | MySQL 8.0                         |
| ML/AI       | scikit-learn, pandas, NumPy       |
| Auth        | Werkzeug (password hashing)       |

---

## 📁 Project Structure

```
HarvestHub/
├── app.py                  # Main Flask application
├── config.py               # Database & app configuration
├── schema.sql              # MySQL database schema
├── requirements.txt        # Python dependencies
│
├── ml/                     # Machine Learning modules
│   ├── recommender.py      # Crop recommendation engine
│   └── price_predictor.py  # Price prediction model
│
├── data/
│   └── crop_prices.csv     # Historical crop price dataset
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout template
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── marketplace.html    # Crop marketplace
│   ├── crop_detail.html    # Single crop details
│   ├── farmer_dashboard.html # Farmer dashboard
│   ├── add_crop.html       # Add new crop
│   ├── edit_crop.html      # Edit crop listing
│   ├── cart.html           # Shopping cart
│   ├── orders.html         # Order history
│   ├── recommend.html      # Crop recommendation page
│   └── predict.html        # Price prediction page
│
└── static/
    ├── css/
    │   └── style.css       # Application styles
    └── js/
        └── main.js         # Client-side JavaScript
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **MySQL Server 8.0**
- **pip** (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/HarvestHub.git
cd HarvestHub
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Database

Update `config.py` with your MySQL credentials:

```python
MYSQL_HOST     = 'localhost'
MYSQL_USER     = 'root'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB       = 'harvesthub'
```

### 4. Create the Database

Run the schema file to set up the database and tables:

```bash
mysql -u root -p < schema.sql
```

### 5. Run the Application

```bash
python app.py
```

The app will be available at **http://localhost:5000**

---

## 📸 Application Modules

| Module               | Route              | Description                          |
|----------------------|--------------------|--------------------------------------|
| Landing Page         | `/`                | Home page with app overview          |
| Register             | `/register`        | Create farmer or buyer account       |
| Login                | `/login`           | User authentication                  |
| Marketplace          | `/marketplace`     | Browse and search available crops    |
| Farmer Dashboard     | `/farmer/dashboard`| Manage crops and view orders         |
| Add Crop             | `/farmer/add_crop` | List a new crop for sale             |
| Shopping Cart        | `/cart`            | View and manage cart items           |
| Place Order          | `/order/place`     | Convert cart to orders               |
| Crop Recommendation  | `/recommend`       | AI-powered crop suggestion           |
| Price Prediction     | `/predict`         | ML-based crop price forecasting      |

---

## 🤖 ML Models

### Crop Recommendation
A **rule-based expert system** that evaluates:
- Soil type (clay, sandy, loamy, black, red)
- Temperature (°C)
- Rainfall (mm)
- Season (Kharif, Rabi, Zaid)

Returns the best crop along with a confidence score and farming tips.

### Price Prediction
A **Linear Regression model** trained on historical crop price data (`data/crop_prices.csv`). Predicts future prices based on:
- Crop name
- Year
- Month

---

## 👥 Team

| Name            | Role                  |
|-----------------|-----------------------|
| Your Name       | Full-Stack Developer  |

---

## 📄 License

This project is developed for academic purposes as part of an **Integrated Online Marketplace Platform (IOMP)** project.

---

## 🙏 Acknowledgements

- [Flask Documentation](https://flask.palletsprojects.com/)
- [scikit-learn](https://scikit-learn.org/)
- [MySQL](https://www.mysql.com/)
