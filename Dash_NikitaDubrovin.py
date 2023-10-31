from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children='dash country', style={'textAlign': 'center'}),
    dcc.Dropdown(
        options=[{'label': year, 'value': year} for year in df['year'].unique()],
        value=df['year'].max(),
        id='year-selection'
    ),
    dcc.Dropdown(
        options=[{'label': country, 'value': country} for country in df['country'].unique()],
        value=['Canada'],
        multi=True,  # Для множественного выбора стран
        id='dropdown-selection'
    ),
    html.Div([
        html.Label('Choose Y-axis:'),
        dcc.Dropdown(
            options=[
                {'label': 'Population', 'value': 'pop'},
                {'label': 'GDP per Capita', 'value': 'gdpPercap'}
                # Другие числовые меры, которые у вас есть в данных
            ],
            value='pop',  # Значение по умолчанию
            id='y-axis-selection'
        ),
    ]),
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='bubble-chart'),
    dcc.Graph(id='top-population-chart'),
    dcc.Graph(id='continent-population-chart')
])

@app.callback(
    Output('line-chart', 'figure'),
    [Input('dropdown-selection', 'value'),
     Input('y-axis-selection', 'value')]
)
def update_line_chart(selected_countries, y_axis):
    dff = df[df['country'].isin(selected_countries)]
    fig = px.line(dff, x='year', y=y_axis, color='country', title='Comparison of Countries')
    return fig

@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('dropdown-selection', 'value'),
     Input('y-axis-selection', 'value')]
)
def update_bubble_chart(selected_countries, y_axis):
    dff = df[df['country'].isin(selected_countries)]
    fig = px.scatter(dff, x='year', y=y_axis, size='pop', color='country', title='Bubble Chart')
    return fig

@app.callback(
    Output('top-population-chart', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_top_population_chart(selected_countries):
    dff = df[df['country'].isin(selected_countries)]
    top_15 = dff.groupby('country')['pop'].max().nlargest(15).reset_index()
    fig = px.bar(top_15, x='country', y='pop', title='Top 15 Countries by Population')
    return fig

@app.callback(
    Output('continent-population-chart', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_continent_population_chart(selected_countries):
    dff = df[df['country'].isin(selected_countries)]
    fig = px.pie(dff, values='pop', names='continent', title='Population by Continent')
    return fig

if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
