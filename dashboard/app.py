import json
import plotly
import plotly.graph_objs as go
from flask import Flask, render_template, request, Response
import data_manager

app = Flask(__name__, static_folder="assets")

ollascomunesdb = data_manager.OllasComunesDB()


@app.route("/data/tweets_plot")
def plot_tweets_ollascomunes():
    comuna = request.args.get('comuna')
    df = ollascomunesdb.get_tweets_comuna(comuna)
    # tweets_links = [f"https://twitter.com/twitter/status/{id}" for id in df['id']]
    data = [
        go.Scatter(
            x=df['datetime'],
            y=df['user_followers_count'],
            text=df['hover_text'],
            mode='markers',
        )
    ]
    # return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder), tweets_links
    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data/last_tweets")
def last_tweets_id_comuna():
    comuna = request.args.get('comuna')
    return json.dumps({
        'latest_tweets_ids': ollascomunesdb.last_tweets_id_comuna(comuna, 15)
    })


@app.route('/data/comunas')
def get_lista_comunas():
    return json.dumps({
        'comunas': ollascomunesdb.get_lista_comunas()
    }, ensure_ascii=False).encode('utf8')


@app.route('/time_feed')
def time_feed():
    def generate():
        yield ollascomunesdb.get_last_update_string()  # return also will work

    return Response(generate(), mimetype='text')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
