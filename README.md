# E-commerce Flask Application

This is a simple e-commerce web application built with Flask and MySQL.

## Features

*   Customer registration and login
*   Supplier registration and login
*   Product browsing
*   Shopping cart functionality
*   Order placement

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-project-name.git
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    *   Make sure you have MySQL installed and running.
    *   Create a database named `ecom`.
    *   Import the provided `.sql` file to set up the tables.

5.  **Create a `.env` file** and add the following environment variables:
    ```
    SECRET_KEY='your_secret_key'
    MYSQL_HOST='your_mysql_host'
    MYSQL_USER='your_mysql_user'
    MYSQL_PASSWORD='your_mysql_password'
    MYSQL_DB='your_mysql_db'
    MYSQL_PORT=your_mysql_port
    ```

6.  **Run the application:**
    ```bash
    flask run
    ```