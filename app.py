import os
import certifi
from flask import Flask
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


# Factory
def create_app():
    app = Flask(__name__)
    client = MongoClient(os.getenv("MONGOD_URI"), tlsCAFile=certifi.where())
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    app.db = client.get_default_database()

    app.register_blueprint(pages)
    return app
