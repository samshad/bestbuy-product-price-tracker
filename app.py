from flask import Flask, request, jsonify
from data_cleaner import DataCleaner
from db_mongo import MongoDBClient
from product_scraper import ProductScraper
from db_postgres import PostgresDBClient

app = Flask(__name__)

# Initialize the MongoDB client
mongo_client = MongoDBClient()


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    return jsonify({"status": "healthy"})


@app.route('/scrape', methods=['POST'])
def scrape_and_store():
    """
    Accept a POST request with a JSON body containing a URL.
    Calls the scraper to get product data, cleans it, and stores it in MongoDB.

    Request JSON format:
    {
        "url": "product_page_url"
    }

    Returns:
        JSON response with success or failure status.
    """

    table_name = "products"

    try:
        # Parse the URL from the request data
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Scrape the product data
        scraper = ProductScraper(url)
        raw_data = scraper.scrape()

        if not raw_data:
            return jsonify({"error": "Failed to scrape data from the URL"}), 500

        # Clean the data
        cleaner = DataCleaner()
        product_details = cleaner.clean_product_data([raw_data])[0]  # Clean single item

        print("Product Details:", product_details)

        product_details["price"] = int(cleaner.clean_and_convert_amount(product_details["price"]) * 100)  # Convert price to cents
        product_details["save"] = int(cleaner.clean_and_convert_amount(product_details["save"]) * 100)  # Convert price to cents

        # Insert the data into PostgreSQL
        db_client = PostgresDBClient()
        inserted_id = db_client.insert_data(table_name, product_details)
        if not inserted_id:
            return jsonify({"error": "Failed to insert data into the PostgreSQL database"}), 500

        data_mongo = {
            "web_code": product_details["web_code"],
            "price": product_details["price"],
            "save": product_details["save"],
            "date": product_details["date"]
        }

        # Insert the cleaned data into MongoDB
        inserted_id = mongo_client.insert_data(data_mongo)
        if not inserted_id:
            return jsonify({"error": "Failed to insert data into the MongoDB database"}), 500

        # Return success response
        return jsonify({"success": True, "inserted_data_postgres": product_details}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
