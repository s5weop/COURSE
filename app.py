from flask import Flask, render_template, url_for, request, redirect, session, send_from_directory
from graphics import creatiDiagram

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "very_SECRET_KEY"

@app.route('/', methods=['POST', 'GET'])
def index():
    files = creatiDiagram()
    return render_template('main.html', numbers = files)

if __name__ == '__main__':
    app.run(debug=True)