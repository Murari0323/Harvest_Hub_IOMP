-- =============================================================
-- HarvestHub — Database Schema
-- =============================================================
-- Run this file once to create the database and tables:
--   mysql -u root -p < schema.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS harvesthub;
USE harvesthub;

-- -----------------------------------------------------------
-- 1. Users (farmers & buyers)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    email       VARCHAR(150)  NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,           -- bcrypt hash
    role        ENUM('farmer','buyer') NOT NULL,
    location    VARCHAR(200)  DEFAULT '',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 2. Crops (listed by farmers)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS crops (
    crop_id     INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id   INT           NOT NULL,
    crop_name   VARCHAR(100)  NOT NULL,
    quantity    DECIMAL(10,2) NOT NULL DEFAULT 0,
    price       DECIMAL(10,2) NOT NULL DEFAULT 0,
    category    VARCHAR(50)   DEFAULT 'General',
    season      VARCHAR(50)   DEFAULT '',
    description TEXT          DEFAULT NULL,
    image_url   VARCHAR(300)  DEFAULT '',
    status      ENUM('available','sold_out') DEFAULT 'available',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 3. Orders
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id     INT           NOT NULL,
    crop_id      INT           NOT NULL,
    farmer_id    INT           NOT NULL,
    quantity     DECIMAL(10,2) NOT NULL,
    total_price  DECIMAL(12,2) NOT NULL,
    order_status ENUM('pending','confirmed','shipped','delivered','cancelled')
                 DEFAULT 'pending',
    order_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id)  REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id)   REFERENCES crops(crop_id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 4. Predictions (price prediction log)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id   INT AUTO_INCREMENT PRIMARY KEY,
    crop_name       VARCHAR(100)  NOT NULL,
    predicted_price DECIMAL(10,2) NOT NULL,
    prediction_date DATE          NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 5. Recommendations (crop recommendation log)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    soil_type         VARCHAR(50)  NOT NULL,
    temperature       DECIMAL(5,2) DEFAULT NULL,
    rainfall          DECIMAL(7,2) DEFAULT NULL,
    season            VARCHAR(50)  NOT NULL,
    recommended_crop  VARCHAR(100) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
