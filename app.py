from os import environ
from flask import Flask, render_template, url_for, jsonify, make_response, request, session

from spacy import en as SpacyModel

from google.cloud import language as GoogleModel

from watson_developer_cloud import AlchemyLanguageV1

alchemy_language = AlchemyLanguageV1(api_key='PUT_YOUR_OWN_KEY')

class GenericEngine:
    
    def parse_input(self, input):
        ## CUSTOM METHOD
        self.get_tokens(input)

        ret = {"arcs": list(), "words": list(), "sentiment": self.sentiment}

        for token in self.tokens:
            arc = self.add_arc(token)
            word = self.add_word(token)
            if isinstance(arc, list):
                ret["arcs"].extend(arc)
            elif arc is None:
                pass
            elif arc.get("start") != arc.get("end"):
                ret["arcs"].append(arc)
            ret["words"].append(word)

        return ret

class WatsonEngine(GenericEngine):

    def __init__(self):
        self.client = AlchemyLanguageV1(api_key='584bb6cc4ec52f2fd73ec69332c4a4ef2cd3c7c6')
        self.parse = self.client.combined
        self.sentiment = None

    def get_tokens(self, input):
        doc = self.parse(text=input, extract='entities,keywords,relations,typed-rels,doc-sentiment')
        index = 0
        words = input.split(' ')
        self.tokens = list()
        self.sentiment = doc.get('docSentiment')

        for relation in doc.get('relations'):
            action = relation.get('action')
            object_ = relation.get('object')
            subject = relation.get('subject')

            if action:
                action.update({"type": "action"})
                action["index"] = input.find(action.get('text'))
                action["subject"] = subject
                action["object"] = object_
                if action not in self.tokens:
                    self.tokens.append(action)

            if object_:
                object_.update({"type": "object"})
                object_["index"] = input.find(object_.get('text'))
                if object_ not in self.tokens:
                    self.tokens.append(object_)

            if subject:
                subject.update({"type": "subject"})
                subject["index"] = input.find(subject.get('text'))
                if subject not in self.tokens:
                    self.tokens.append(subject)

        self.tokens.sort(key=lambda token: token.get('index'))
        for i, token in enumerate(self.tokens):
            token.update({'index': i})

        for token in [token for token in self.tokens if token.get('type') == 'action']:
            if token.get('subject'):
                subject_index = self.tokens.index(token["subject"])
                token["subject"] = subject_index
            if token.get('object'):
                object_index = self.tokens.index(token["object"])
                token["object"] = object_index

    def add_arc(self, token):
        if token.get('type') == 'action':
            return [{
                "start": token.get('subject'),
                "end": token.get('index'),
                "label": "subj",
                "dir": "left" if token.get('index') < token.get('subject') else 'right'
            },{
                "start": token.get('index'),
                "end": token.get('object', token.get('index')),
                "label": "obj",
                "dir": "left" if token.get('object', 0) < token.get('index') else 'right'
            }]
        else:
            return None

    def add_word(self, token):
        return {
            "tag": token.get('type'),
            "text": token.get('text'),
            "lemma": token.get('lemmatized', 'None')
        }

class GoogleEngine(GenericEngine):

    def __init__(self):
        self.client = GoogleModel.Client()
        self.parse = self.client.document_from_text
        self.sentiment = None

    def get_tokens(self, input):
        doc = self.parse(input)
        (self.sentences, self.tokens, sentiment, self.entities) = doc.annotate_text()

        self.sentiment = {
            "score": sentiment.score,
            "magnitude ": sentiment.magnitude
        }

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
        self.sentiment = None

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
    "watson": WatsonEngine()
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
	app.run(host='127.0.0.1', port=4848, debug=True, use_reloader=False)
