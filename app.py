from os import environ

from flask import Flask, render_template, url_for, jsonify, make_response, request, session

from spacy import en

class Engine:

    def load(self):
        self.nlp = en.English()

    def parse_input(self, input):

        def add_arc(token):
            return {
                "start": token.i if token.i < token.head.i else token.head.i,
                "end": token.i if token.i > token.head.i else token.head.i,
                "label": token.dep_,
                "dir": "left" if token.i < token.head.i else "right"
            }
            
        def add_word(token):
            return {
                "tag": token.tag_,
                "pos": token.pos_,
                "text": token.text,
                "lemma": token.lemma_
            }

        doc = self.nlp(input)
        ret = {"arcs": list(), "words": list()}
        for token in doc:
            new_arc = add_arc(token)
            if new_arc["start"] != new_arc["end"]:
                ret["arcs"].append(new_arc)
            ret["words"].append(add_word(token))

        return ret


#### CREATE APPLICATION OBJECT
app = Flask(__name__, template_folder='static/', static_url_path='', static_folder='static/')


#### COMPILE SASS FOR UI
# assets = Environment(app)
# assets.url = app.static_url_path
# scss = Bundle('css/style.sass', filters='pyscss', output='all.css')
# assets.register('scss_all', scss)


#### LOAD SPACY MODEL
engine = Engine()
engine.load()


@app.route('/parse', methods=['POST'])
def parse():
    ret = engine.parse_input(request.form.get('input'))
    return make_response(jsonify({"data": ret, "status": 200}))

@app.route('/', methods=['GET', 'POST'])
def main():
	return render_template("index.html")

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=4848, debug=True, use_reloader=True)
