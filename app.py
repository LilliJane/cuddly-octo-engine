from os import environ

from flask import Flask, render_template, url_for, jsonify, make_response, request, session

from spacy import en as SpacyModel

from google.cloud import language as GoogleModel

class GenericEngine:
    
    def parse_input(self, input):
        ## CUSTOM METHOD
        self.get_tokens(input)

        ret = {"arcs": list(), "words": list()}
        for token in self.tokens:
            arc = self.add_arc(token)
            word = self.add_word(token)
            if arc["start"] != arc["end"]:
                ret["arcs"].append(arc)
            ret["words"].append(word)
        return ret



class GoogleEngine(GenericEngine):

    def __init__(self):
        self.client = GoogleModel.Client()
        self.parse = self.client.document_from_text

    def get_tokens(self, input):
        doc = self.parse(input)
        (self.sentences, self.tokens, self.sentiment, self.entities) = doc.annotate_text()
        for i, token in enumerate(self.tokens):
            token.text_begin = i

    def add_arc(self, token):
        return {
            "start": token.text_begin if token.text_begin < token.edge_index else token.edge_index,
            "end": token.text_begin if token.text_begin > token.edge_index else token.edge_index,
            "label": token.edge_label,
            "dir": "left" if token.text_begin < token.edge_index else "right"
        }

    def add_word(self, token):
        return {
            "tag": token.part_of_speech,
            "pos": token.part_of_speech,
            "text": token.text_content,
            "lemma": token.lemma
        }



class SpacyEngine(GenericEngine):

    def __init__(self):
        self.parse = SpacyModel.English()

    def get_tokens(self, input):
        self.tokens = self.parse(input)

    def add_arc(self, token):
        return {
            "start": token.i if token.i < token.head.i else token.head.i,
            "end": token.i if token.i > token.head.i else token.head.i,
            "label": token.dep_,
            "dir": "left" if token.i < token.head.i else "right"
        }
        
    def add_word(self, token):
        return {
            "tag": token.tag_,
            "pos": token.pos_,
            "text": token.text,
            "lemma": token.lemma_
        }

#### CREATE APPLICATION OBJECT
app = Flask(__name__, template_folder='static/', static_url_path='', static_folder='static/')


#### LOAD MODELS
print("Loading engines...")
engines = {
    "spacy": SpacyEngine(),
    "google": GoogleEngine(),
}

#### API ROUTES
@app.route('/parse', methods=['POST'])
def parse():
    using = request.form.get("engine")
    if using in engines:
        ret = engines[using].parse_input(request.form.get('input'))
        return make_response(jsonify({"data": ret, "status": 200}))
    else:
        return make_response(jsonify({"data": "Wrong processing engine", "status": 400}))

@app.route('/', methods=['GET', 'POST'])
def main():
	return render_template("index.html")

#### RUNNING THE APP
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=4848, debug=True, use_reloader=True)
