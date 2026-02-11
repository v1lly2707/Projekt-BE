
# PrestaShop E-commerce Project

## 📝 Project Overview

This project focuses on the practical application, configuration, and deployment of an open-source e-commerce solution using **PrestaShop 1.7.8**. The goal was to simulate a real-world developer environment, covering the full lifecycle from data scraping and local development to containerized deployment on a cluster and integration with analytical tools.

## 👥 Team Members

-   Natalia Sekula
-   Natalia Dembkowska
-   Olga Rodziewicz
-   Patryk Lewandowski
-   Filip Świniarski
    

## 🛠 Tech Stack

-   **Core:** PrestaShop 1.7.8.x
    
-   **Infrastructure:** Docker, Docker-Compose, Ubuntu LTS
    
-   **Database:** MariaDB / MySQL
    
-   **Automation:** Selenium (UI Testing), Python/Node.js (Scraping)
    
-   **Analytics:** Google Analytics 4 (GA4)
    
-   **Networking:** HTTPS (Self-signed SSL), SSH Tunnels
    

----------

## 🚀 Getting Started (Deployment)

### Prerequisites

-   Docker & Docker-Compose installed.
    
-   Access to the student cluster (for production branch).
    


## 🔍 Features Implementation

### 1. Data Scraping & API Import

-   **Automated Scrapper:** Custom tool to extract products, categories (min. 4 main, 2 subcategories each), and high-quality images.
    
-   **REST API:** Products were automatically initialized in the store via PrestaShop API based on the scrapped JSON/CSV data.
    
-   **Inventory:** Over 1000 products registered with realistic descriptions and stock limits (max 10 units per item).
    

### 2. Store Configuration

-   **Localization:** Fully translated into Polish.
    
-   **Payments:** Configured for Polish market standards (Cash on Delivery, Bank Transfer).
    
-   **Shipping:** * Two custom carriers defined.
    
    -   Free shipping for orders above 2000 PLN.
        
    -   Weight limit (max 50kg) implemented to restrict heavy shipping.
        
-   **SSL:** All traffic forced through HTTPS using a self-signed certificate.
    

### 3. Analytics (GA4)

Integrated **Google Analytics 4** with custom event tracking:

-   **Destination Goal:** Tracked user arrivals at the registration success page.
    
-   **Event Goal:** Custom event triggered when a user clicks a promotional banner or adds a discounted product to the cart.
    
-   **Data Flow:** E-commerce tracking enabled to monitor order values and conversion history.
    

### 4. Automated UI Tests (Selenium)

The test suite performs the following in under 5 minutes:

1.  Adding 10 products from different categories to the cart.
    
2.  Searching for a product by name and adding a random result.
    
3.  Deleting 3 items from the cart.
    
4.  User registration and checkout process.
    
5.  Verification of order status and VAT invoice download.
    

----------

## 🔄 CI/CD Pipeline

A configuration file is included to trigger a pipeline on every `push` to the `main` branch.

-   **Build:** Automatically creates a new Docker image of the store.
    
-   **Validation:** Ensures the production-ready code is always captured in the registry.
    
