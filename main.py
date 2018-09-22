import base64
import datetime
import io
import struct

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import plotly.graph_objs as go
from argparse import ArgumentParser
import pandas as pd
from librosa.core import load
import wave


import ipdb


app = dash.Dash()

app.scripts.config.serve_locally = True

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    print(filename, date)
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.wav'):
    
            # Assume that the user uploaded a CSV file
            # df = pd.read_csv(
            #     io.StringIO(decoded.decode('utf-8')))
            with wave.open(io.BytesIO(decoded), 'rb') as file:
                astr = file.readframes(file.getnframes())
                audio = struct.unpack("%ih" % (file.getnframes()* file.getnchannels()), astr)
                file.close()
            # audio, sr = load(list(io.BytesIO(decoded)))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
            dcc.Graph(figure={
                'data': [dict(x=len(audio), y=audio)],
                'layout': go.Layout(title='Order Status by Customer')
            }),
            dcc.Slider()
        ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        # children = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return children[0]


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-i', '--ip', dest='ip', default="localhost")
    ap.add_argument('-p', '--port', dest='port', default=8008)
    args = ap.parse_args()
    app.run_server(debug=True, host=args.ip, port=args.port)