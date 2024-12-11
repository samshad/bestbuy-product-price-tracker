# bestbuy-product-price-tracker

## Overview
This project is a web application built with Flask that provides various endpoints to manage and retrieve product data from a PostgreSQL and MongoDB database. It includes functionalities for scraping product details, storing them, and retrieving product and price information.

## Features
- Health check endpoint
- Scrape and store product details
- Retrieve all products
- Retrieve product details by web code or product ID
- Retrieve product prices over the time by web code

## Technologies Used
- Python
- Flask
- Playwright
- BeautifulSoup
- PostgreSQL (Neon)
- MongoDB (Atlas)
- Docker

## Setup and Installation

### Prerequisites
- Python 3.12+
- Docker
- PostgreSQL
- MongoDB

### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/samshad/bestbuy-product-price-tracker.git
    cd bestbuy-product-price-tracker
    ```

2. Build and run the project using Docker Compose:
    ```sh
    docker-compose up -d
    ```

3. Access the application at `http://localhost:5000`.

## Usage

### Running the Application
1. Start the Flask application:
    ```sh
    flask run
    ```

2. The application will be available at `http://localhost:5000`.

### API Endpoints

#### Health Check
- **GET** `/health`
    - Returns the health status of the application.

#### Scrape and Store Product Details
- **POST** `/scrape`
    - Payload:
        ```json
        {
            "web_code": "string",
            "url": "string"
        }
        ```
    - Scrapes and stores product details using the provided web code or URL.

#### Get All Products
- **GET** `/products`
    - Retrieves all product details from the database.

#### Get Product Details
- **GET** `/product`
    - Query Parameters:
        - `web_code`: The web code of the product.
        - `product_id`: The ID of the product.
    - Retrieves product details by web code or product ID.

#### Get Product Prices
- **GET** `/product-prices`
    - Query Parameters:
        - `web_code`: The web code of the product.
    - Retrieves all price details for a product by its web code.


## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements
- [Flask](https://flask.palletsprojects.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [MongoDB](https://www.mongodb.com/)