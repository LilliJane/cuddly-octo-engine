
$("#input").keyup(function(event){
    if(event.keyCode == 13){
    	process();
    }
});

const displacy = new displaCy('http://localhost:4848', {
    container: '#displacy',
    format: 'spacy',
	collapsePunct: true,
    collapsePhrase: true,
    distance: 200,
    offsetX: 150,
    arrowSpacing: 10,
    arrowWidth: 8,
    arrowStroke: 2,
    wordSpacing: 40,
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

show_details = function(word, tokens) {
	$.each(tokens, function(index, token) {
		if (token.text == word) {
			console.log(token)
			$("#details").text(JSON.stringify(token, null, 2))
		}
	});
}

process = function() {
	text_to_process = $("#input").val();
	if (text_to_process !== undefined && text_to_process.length > 0) {
		
		$.post('/parse', {
			"input": text_to_process
		}).then(function(parsed) {
			console.log(parsed.data)
			displacy.render(parsed.data, {
			    arrowSpacing: 50
			});
			$(".displacy-token").click(function() {
				show_details(this.children[0].textContent, parsed.data.words)
			});
		});
	}



}