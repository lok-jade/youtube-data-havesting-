YouTube Data harvesting 
This project is designed to scrape data from YouTube, store the data in MongoDB, transfer it to a PostgreSQL database, and visualize it using a Streamlit app.

Table of Contents
Introduction
Features
Installation
Usage
Project Structure
Technologies Used
Contributing
License
Introduction
This project aims to scrape comment data from YouTube videos and store it in MongoDB. The data is then transferred to a PostgreSQL database for structured storage and further processing. Finally, the data is visualized using a Streamlit app, providing an easy-to-use interface to explore the scraped data.

Features
Scrape YouTube Comments: Extract comments from YouTube videos.
Store Data in MongoDB: Initial storage of unstructured data in MongoDB.
Transfer Data to PostgreSQL: Structured storage and processing in PostgreSQL.
Visualize Data with Streamlit: Interactive web application to explore the data.
Installation
Clone the repository

bash
Copy code
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
Set up a virtual environment

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install the required dependencies

bash
Copy code
pip install -r requirements.txt
Set up MongoDB and PostgreSQL

Ensure MongoDB and PostgreSQL are installed and running on your local machine or server.
Create a PostgreSQL database named youtube_scrape.
Configuration

Update the database configuration settings in the project as needed.
Usage
Scrape YouTube Data

Modify and run the script to scrape data from YouTube and store it in MongoDB.
python
Copy code
python youtube_scrape.py
Transfer Data to PostgreSQL

Run the script to transfer data from MongoDB to PostgreSQL.
python
Copy code
python transfer_to_postgres.py
Run the Streamlit App

Start the Streamlit app to visualize the data.
bash
Copy code
streamlit run app.py
Project Structure
lua
Copy code
|-- README.md
|-- requirements.txt
|-- youtube_scrape.py          # Script for scraping YouTube data
|-- transfer_to_postgres.py    # Script for transferring data to PostgreSQL
|-- app.py                     # Streamlit app script
Technologies Used
Python: The primary programming language used for this project.
pandas: Data manipulation and analysis.
pymongo: MongoDB client for Python.
psycopg2: PostgreSQL database adapter for Python.
Streamlit: Framework for creating interactive web applications.
YouTube Data API: API to fetch data from YouTube.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License.