function render_tweets() {
    // Fuente: https://www.labnol.org/code/19933-embed-tweet-with-javascript
    $('.tweet').each(function () {
        var tweet = $(this)[0];
        var id = $(this).attr("id");

        twttr.widgets.createTweet(
            id, tweet,
            {
                conversation: 'none',    // or all
                cards: 'visible',  // or visible
                linkColor: '#cc0000', // default is blue
                theme: 'light'    // or dark
            })
            .then(function (el) {
                el.contentDocument.querySelector(".footer").style.display = "none";
            });
    });
}

function update_tweets_plot(comuna) {
    $.get("/data/tweets_plot", {comuna: comuna}, function(graphs) {
        // todo add links

        var layout = {
            title:'Tweet emitidos sobre ollas comunes los últimos 7 días',
            xaxis:{
                title:'Fecha'
            },
            yaxis: {
                title:'Cantidad de seguidores del twittero'
            },
            autosize:true
        };
        // Plotly.plot('bargraph',graphs,layout, {responsive: true});
        var tweets_plot = document.getElementById('bargraph');

        Plotly.newPlot(tweets_plot,graphs,layout, {responsive: true});

        tweets_plot.on('plotly_click', function(data){
            if (data.points.length === 1) {
                // Note: window navigation here.
                // window.location = links[data.points[0].pointNumber];

                var win = window.open(links[data.points[0].pointNumber], '_blank');
                win.focus();
            }})
    }, "json");
}

function update_latest_tweets(comuna) {
    $.get('/data/last_tweets', {comuna: comuna}, function (data) {
        $('#latest-tweets').empty();
        var ids = data.latest_tweets_ids;
        console.log(ids);
        ids.forEach(function (item, index) {
            $('#latest-tweets').append(`<div class="tweet" id=${item}></div>`)
        });
        render_tweets();
    },'json');

}



$(document).ready(function() {
    $.get("/data/comunas", function(data){
        var parsed_data = JSON.parse(data);
        var comunas = parsed_data.comunas;
        $.each(comunas, function(key, modelName){
            //Use the Option() constructor to create a new HTMLOptionElement.
            var option = new Option(modelName, modelName);
            //Convert the HTMLOptionElement into a JQuery object that can be used with the append method.
            $(option).html(modelName);
            //Append the option to our Select element.
            $('#select-comuna').append(option)
        });

    });

    $.get("data/last_update", function (data) {
        var parsed_data = JSON.parse(data);
        $('#ultima-actualizacion').html("Última actualización: " + parsed_data.last_update);
    })

    $("#info-comunas").tooltip({
        'selector': '',
        'placement': 'top',
        'container':'body'
    });



});

$("#select-comuna").change(function(){
    var comuna = $("#select-comuna").val();

    update_tweets_plot(comuna);
    update_latest_tweets(comuna);
});

$(document).ready(function () {

});