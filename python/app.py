# Flask endpoints for our react fron-end
from flask import Flask, send_file
from flask_cors import CORS
from main import main_bytes_image
app = Flask(__name__)
CORS(app)


@app.route('/plots', methods=['GET'])
def send_plot():
    bytes_obj = main_bytes_image(iterations=1000, width=100, height=100)

    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=False)
