
$("#input").keyup(function(event){
    if(event.keyCode == 13){
    	process();
    }
});

const displacy = new displaCy('http://localhost:4848', {
    container: '#displacy',
    format: 'spacy',
    distance: 300,
    offsetX: 100,
    bg: "#272822"
});

const parse = {
    arcs: [
        { dir: 'left', end: 0, label: 'npadvmod', start: 1 }
    ],
    words: [
        { tag: 'UH', text: 'Hello' },
        { tag: 'NNP', text: 'World.' }
    ]
};

console.log(displacy)

process = function() {
	text_to_process = $("#input").val();
	if (text_to_process !== undefined && text_to_process.length > 0) {
		
		$.post('/parse', {
			"input": text_to_process
		}).then(function(parsed) {
			console.log(parsed.data)
			displacy.render(parsed.data, {
			    color: '#ff0000'
			});

		});
	}
}