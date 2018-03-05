from flask import Flask

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///tabletennis_stat.db'
DATABASE_CONNECT_OPTIONS = {}

from sqlalchemy import create_engine
conn = create_engine(os.environ['DB_URI'])

import dash
app = dash.Dash()

# Run a test server.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True)