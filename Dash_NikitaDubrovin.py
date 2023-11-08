from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_draggable

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = ['https://raw.githubusercontent.com/TomTomen/py/main/styles.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(style={'height': '150vh'}, children=[
    html.H1(children='Страны Dash Дубровин Н.А', style={'textAlign': 'center'}),
    html.Div([html.Label('Выберите страну:'),
              dcc.Dropdown(df.country.unique(), value='Canada', multi=True, id='dropdown-selection')],
             style={'width': '49%', 'display': 'inline-block'}),
    html.Div([], style={'width': '2%', 'display': 'inline-block'}),
    html.Div([html.Label('Выберите данные:'),
              dcc.Dropdown(['lifeExp', 'pop', 'gdpPercap'], value='pop', id='dropdown-selection_2')],
             style={'width': '49%', 'display': 'inline-block'}),

    dash_draggable.ResponsiveGridLayout([
        dcc.Graph(id='graph-content', style={'width': '100%', 'height': '100%'}),
        dcc.Graph(id='top-population', style={'width': '100%', 'height': '100%'})
    ], ),

    dash_draggable.ResponsiveGridLayout([
        html.Div([
            html.Div([
                html.Label('Выберите цвет:'),
                dcc.RadioItems(
                    id='radio-selection',
                    options=['country', 'continent'],
                    value='continent',
                    inline=True
                )
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Выберите Y:'),
                dcc.Dropdown(['lifeExp', 'pop', 'gdpPercap'], value='pop', id='dropdown-selection_Y')
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Выберите X:'),
                dcc.Dropdown(['lifeExp', 'pop', 'gdpPercap'], value='pop', id='dropdown-selection_X')
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Выберите Размер:'),
                dcc.Dropdown(['lifeExp', 'pop', 'gdpPercap'], value='pop', id='dropdown-selection_Size')
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Label(dcc.Graph(id='pie-pop', style={'width': '100%'}))
        ], style={'height': '100%'}),

        dcc.Graph(id='bubble-chart')
    ]),

    dcc.RangeSlider(id='year-slider', marks={str(year): str(year) for year in df['year']},  # Метки для ползунка
                    min=df['year'].min(),
                    max=df['year'].max(),
                    step=1,  # Шаг для ползунка
                    value=[1978, 2018]  # Значения по умолчанию
                    )
])


# app.css.append_css({"external_url": "https://raw.githubusercontent.com/TomTomen/py/main/styles.css"})
@app.callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dropdown-selection_2', 'value'),
    Input('year-slider', 'value')

)
def update_graph(selected_country, measure, selected_years):
    if not isinstance(selected_country, list):
        selected_country = [selected_country]
    dff = df[df['country'].isin(selected_country)]
    dff = dff[(dff['year'] >= selected_years[0]) & (dff['year'] <= selected_years[1])]
    return px.line(dff, x='year', y=measure, color='country')


@app.callback(
    Output('top-population', 'figure'),
    Input('dropdown-selection_2', 'value'),
    Input('year-slider', 'value'),
    Input('graph-content', 'clickData')

)
def update_bar(measure, selected_years, point):
    dff = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
    if not point is None:
        value = point['points'][0]['x']
        dff = dff[dff.year == value]
    dff = dff.groupby('country').sum()[[measure]].sort_values(measure, ascending=False)[:15]
    return px.bar(dff)


@app.callback(
    Output('pie-pop', 'figure'),
    Input('year-slider', 'value'),
    Input('graph-content', 'clickData'),
    Input('radio-selection', 'value'),
    Input('dropdown-selection_X', 'value'),
    Input('dropdown-selection_Y', 'value'),
    Input('dropdown-selection_Size', 'value')
)
def update_pie(selected_years, point, selected_radio, x, y, size):
    dff = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

    if point is not None:
        value = point['points'][0]['x']
        dff = dff[dff['year'] == value]

    if selected_radio == 'continent':
        fig = px.scatter(dff, x=x, y=y,
                         size=size, color="continent", hover_name="continent",
                         log_x=True, size_max=55)
        title = 'Континенты'
        return fig
    else:
        fig = px.scatter(dff, x=x, y=y,
                         size=size, color="country", hover_name="country",
                         log_x=True, size_max=55)
        title = 'Страны'
        return fig


#        dff = dff.groupby('country').sum()['pop']
#        values = dff.values
#        names = dff.index.tolist()
#        return px.pie(values=values[:7], names=names[:7])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('graph-content', 'clickData')

)
def update_graph(selected_years, point):
    dff = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
    if not point is None:
        value = point['points'][0]['x']
        dff = dff[dff.year == value]
    values = dff.groupby('continent').sum()['pop'].values
    names = dff.groupby('continent').sum()['pop'].index.tolist()
    return px.pie(dff, values=values, names=names)


if __name__ == '__main__':
    app.run()
