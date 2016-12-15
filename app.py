from os import environ

from flask import Flask, render_template, url_for, jsonify, make_response

app = Flask(__name__, template_folder='static/', static_url_path='', static_folder='static/')

@app.route('/parse/<sentence>')
def parse(sentence):
    return make_response(jsonify("OK", 200))

@app.route('/', methods=['GET', 'POST'])
def main():
	return render_template("index.html")

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=4848, debug=True, use_reloader=True)
