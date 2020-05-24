import datetime

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import data_manager

#


bbdd_ollas_comunes = data_manager.get_ollascomunes_df()
comunas = bbdd_ollas_comunes['COMUNA']

app = dash.Dash('app')
app.title = 'Ollas comunes Chile'

# app.scripts.config.serve_locally = False
# dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'
app.layout = html.Div([
    dcc.Interval(id='timer', interval=60*1000),
    html.H1('Ollas comunes por comuna en tiempo real, Twitter'),
    html.H4(
        children='(Última actualización: {})'.format(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')),
        id='ultima_actualizacion'),
    dcc.Dropdown(
        id='comuna_selector',
        options=[
            {'label': comuna, 'value': comuna} for comuna in comunas
        ],
        value='Santiago'
    ),
    dcc.Graph(id='my-graph')
], className="container")


@app.callback(Output('my-graph', 'figure'),
              [Input('comuna_selector', 'value')])
def choose_comuna_graph(selected_dropdown_value):
    tweets_comuna = bbdd_ollas_comunes[bbdd_ollas_comunes['COMUNA'] == selected_dropdown_value]
    fig = px.line(tweets_comuna, x="date", y="retweets", color='username', hover_data=['text'])
    fig.update_traces(mode='markers+lines')
    fig.update_layout(
        title="Cantidad de retweets de tweets emitidos por integrantes del Concejo Municipal de Ñuñoa",
    )
    return fig


@app.callback(Output('ultima_actualizacion', 'children'),
              [Input('timer', 'n_intervals')])
def last_update(n):
    return '(Última actualización: {})'.format(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))


@app.callback(Output('ultima_actualizacion', 'children'),
              [Input('timer', 'n_intervals')])
def last_update(n):
    return '(Última actualización: {})'.format(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))



if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
