
$("#text_input").keyup(function(event){
    if(event.keyCode == 13){
    	process();
    }
});

$(".c-dropdown__option").click(function(elem) {
	$("#".concat(engine)).css('color', 'white');
	$(this).css('color', 'red');
	$("#engine_label").text("Processing with : " + $(this).text());
	engine = $(this).text().toLowerCase();
	$("#engine_label").css("color", "white");
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
    wordSpacing: 80,
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

var engine = "spacy";
$("#spacy").css('color', 'red');

show_sentiment = function(sentiment) {
	$("#sentiment").text(JSON.stringify(sentiment, null, 2));
}

show_details = function(word, parsed) {
	var tokens = parsed.words;
	$.each(tokens, function(index, token) {
		if (token.text == word) {
			$("#details").text(JSON.stringify(token, null, 2))
		}
	});
}

process = function() {
	text_to_process = $("#text_input").val();
	if (text_to_process !== undefined && text_to_process.length > 0) {
		
		$.post('/parse', {
			"input": text_to_process,
			"engine": engine
		}).then(function(parsed) {
			console.log(parsed.data);
			$("sentiment").text("");
			$("details").text("");
			displacy.render(parsed.data, {
			    arrowSpacing: 50
			});
			if (parsed.data.sentiment) {
				show_sentiment(parsed.data.sentiment);
			}
			$(".displacy-token").click(function() {
				show_details(this.children[0].textContent, parsed.data)
			});
		});
	}



}