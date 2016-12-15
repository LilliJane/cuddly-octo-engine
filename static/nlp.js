
const displacy = new displaCy('http://localhost:4848', {
    container: '#displacy',
    format: 'spacy',
    distance: 300,
    offsetX: 100
});

const parse = {
    arcs: [
        { dir: 'right', end: 1, label: 'npadvmod', start: 0 }
    ],
    words: [
        { tag: 'UH', text: 'Hello' },
        { tag: 'NNP', text: 'World.' }
    ]
};

console.log(displacy)

process = function() {
	$.get('/parse/'.concat("bonjour")).then( function() {

		displacy.render(parse, {
		    color: '#ff0000'
		});

	});
}