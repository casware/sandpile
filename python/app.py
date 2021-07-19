# Flask endpoints for our react fron-end
from flask import Flask, json, jsonify
from flask_cors import CORS
from main import main_grid
app = Flask(__name__)
CORS(app)


@app.route('/plots', methods=['GET'])
def send_plot():
    grid = main_grid(iterations=1000, width=100, height=100)

    return jsonify(grid)


if __name__ == '__main__':
    app.run(debug=False)
