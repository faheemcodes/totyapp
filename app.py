import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, date
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input 
import dash_table as dt
import dash_auth
import plotly.graph_objs as go


VALID_USERNAME_PASSWORD_PAIRS = {'toty': '123toty'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

ledgerFile = 'assets/ledgerBackup/ledger.xlsx'

today = date.today()
start_date = date(2021,1,4)

totdf = pd.read_csv('assets/TotalPortfolio.csv')
cppdf = pd.read_csv('assets/totalFund.csv')
sp500 = pd.read_csv('assets/sp500.csv')
historydf = pd.read_csv('assets/stockhistory.csv')

#cppdf = cppdf[cppdf['Date'] >= str(start_date)]
totdf['Name'] = 'DAA Portfolio'

cppdf['Name'], sp500['Name'] = 'CPP Portfolio', 'S&P 500 Index'
cppdf['stockSum'], sp500['stockSum'] = '', ''
cppdf['cashSum'], sp500['cashSum'] = '', ''
base_price = cppdf.iloc[0]['totalSum']
cppdf['Growth'] = cppdf['totalSum']/base_price

base_price = sp500.iloc[0]['totalSum']
sp500['Growth'] = sp500['totalSum']/base_price

finaldf = pd.concat([totdf, cppdf, sp500])

totPercent = round((totdf.iloc[-1]['totalSum']-totdf.iloc[-2]['totalSum'])/totdf.iloc[-2]['totalSum']*100,2)
cppPercent = round((cppdf.iloc[-1]['totalSum']-cppdf.iloc[-2]['totalSum'])/cppdf.iloc[-2]['totalSum']*100,2)
spPercent = round((sp500.iloc[-1]['totalSum']-sp500.iloc[-2]['totalSum'])/sp500.iloc[-2]['totalSum']*100,2)

totGrowth = round((totdf.iloc[-1]['Growth']-1)*100,2)
cppGrowth = round((cppdf.iloc[-1]['totalSum']/cppdf.iloc[0]['totalSum']-1)*100,2)
spGrowth = round((sp500.iloc[-1]['totalSum']/sp500.iloc[0]['totalSum']-1)*100,2)

if totPercent > 0:
    totColor = 'success'
elif totPercent == 0:
    totColor = 'warning'
else:
    totColor = 'danger'

if cppPercent > 0:
    cppColor = 'success'
elif cppPercent == 0:
    cppColor = 'warning'
else:
    cppColor = 'danger'

if spPercent > 0:
    spColor = 'success'
elif spPercent == 0:
    spColor = 'warning'
else:
    spColor = 'danger'

if totGrowth > 0:
    totGrowthColor = 'success'
elif totGrowth == 0:
    totGrowthColor = 'warning'
else:
    totGrowthColor = 'danger'

if cppGrowth > 0:
    cppGrowthColor = 'success'
elif cppGrowth == 0:
    cppGrowthColor = 'warning'
else:
    cppGrowthColor = 'danger'

if spGrowth > 0:
    spGrowthColor = 'success'
elif spGrowth == 0:
    spGrowthColor = 'warning'
else:
    spGrowthColor = 'danger'

inddf = pd.read_csv('assets/IndividualPortfolio.csv')
date = inddf['Date'].unique().max()
inddf.columns = ['Name', 'Stocks', 'Cash', 'Total', 'Date']

ledger = pd.read_excel(ledgerFile, sheet_name = 'Ledger', skiprows = 4, converters= {'Date': pd.to_datetime})
ledger['Date'] = ledger['Date'].dt.date
ledger.sort_values(by=['Date'], inplace=True)
live = ledger[ledger['Status']=='Y']

livedf = live[['Name','Ticker Name']]
livedf.dropna(inplace=True, subset=['Ticker Name'])
nameslist = livedf['Name'].unique()
livedict = dict((i, livedf[livedf['Name']==i]['Ticker Name'].unique().tolist()) for i in nameslist)
#livedict = livedf.to_dict("list")
names = list(livedict.keys())

industrydf = live.groupby('Industry').size().reset_index()
industrydf.columns = ['Industry', 'Count']
leaderboard = inddf[inddf['Date']== str(date)].sort_values(by=['Total', 'Name'], ascending=False)
leaderboard.columns = ['Name', 'Stocks/ETFs', 'Cash', 'Total', 'Date']
leaderboard.insert(0, 'Rank', range(1, 1 + len(leaderboard)))
leaderboard = leaderboard[['Rank', 'Name', 'Stocks/ETFs', 'Cash', 'Total']]
columns = [{"name": i, "id": i} for i in leaderboard.columns]
leaderdf = leaderboard[:5].sort_values(by=['Total'], ascending=True)

tabs_styles = {
    'height': '30px',
    'width' : '45%'
}
tab_style = {
    'padding': '2px',
    'backgroundColor': '#444444',
    'fontColor': 'black',
    'border': '0px solid grey'
}
tab_selected_style = {
    'backgroundColor': '#296d98',
    'color': 'white',
    'padding': '2px',
    'border': '0px solid grey'
}

app.layout = html.Div([
    html.Div(style={'height':75, 'margin-left':400, 'margin-right':400}, children = [
        html.Br(),
        html.H3('Trade of the year !', style={"textAlign": "center", 'color': 'white', 'margin-top':1, 'padding-top': '0rem'}),
        html.Br()
        ], className = 'rows'),

    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Main', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Comparison', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Leaderboard', value='tab-3', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Individual', value='tab-4', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline')
], style={'margin-left':40, 'margin-right':40})

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab1()
    elif tab == 'tab-2':
        return tab2()
    elif tab == 'tab-3':
        return tab3()
    elif tab == 'tab-4':
        return tab4()


def tab1():
    layout = html.Div([
        html.H5('Growth - DAA Portfolio vs CPP Total Fund vs S&P 500 Index', style = {'color': 'orange'}),
        html.Label('The daily prices are indexed to a common starting point of 1 based on the opening prices on 4th Jan 2021. CPP Total Fund values are reported with a one-day lag.', style = {'font-style': 'italic'}),
        dcc.Loading(type = 'dot', children = 
            html.Div([
                dcc.Graph(id='totLineChart', figure={'layout' : {'height': 420}}, style={"width": '80%'}),
                dbc.Card([
                    dbc.CardBody(
                        [
                            dbc.ListGroupItem("Daily Changes", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                            dbc.ListGroupItem("DAA Portfolio : " + str(totPercent) + "%" ,color=totColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                            dbc.ListGroupItem("CPP Total Fund : " + str(cppPercent) + "%" ,color=cppColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                            dbc.ListGroupItem("S&P 500 Index : " + str(spPercent) + "%" ,color=spColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                        ], style={'backgroundColor': 'rgba(0, 0, 0, 0)', 'padding-top': '0rem', 'padding-left': '0rem', 'border':'0px solid black'}),
                    dbc.CardBody(
                        [
                            dbc.ListGroupItem("Overall Growth", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                            dbc.ListGroupItem("DAA Portfolio : " + str(totGrowth) + '%',color=totGrowthColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                            dbc.ListGroupItem("CPP Total Fund : " + str(cppGrowth) + '%',color=cppGrowthColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                            dbc.ListGroupItem("S&P 500 Index : " + str(spGrowth) + '%',color=spGrowthColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                            dbc.ListGroupItem("* from 4th Jan 2021", style={'fontSize': '13px', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'padding-top':'0rem'}),
                        ], style={'backgroundColor': 'rgba(0, 0, 0, 0)', 'padding-top': '0rem', 'padding-left': '0rem', 'border':'0px solid black'}),
                    ],style={"width": "17%", 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'padding-top':'0rem'})
                ], className = 'row', style = {'margin-left':0})
            ),
        html.Br(),
        html.H5('Leaderboard', style = {'color': 'orange'}),
        html.Label('The leaderboard is last updated on ' +  str(date) + ' (opening prices). Check the leaderboard tab for the full table.', style = {'font-style': 'italic'}),
        dcc.Loading(type = 'dot', children =
            html.Div([
                html.Div
                    ([dcc.Graph(id='leaderBarChart', figure={'layout' : {'height': 450, 'margin' : {'t': 500}}})], style = {'margin-left':10}),
                html.Div
                    ([dbc.Card([
                            dbc.CardBody([
                                dbc.ListGroupItem("Total Amount (Stocks/ETFs + Cash)", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                                dbc.ListGroupItem('1 - ' + str(leaderdf.iloc[4]['Name']) + ' : ' + str(round(leaderdf.iloc[4]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 60, 110, 100)'}),
                                dbc.ListGroupItem('2 - ' + str(leaderdf.iloc[3]['Name']) + ' : ' + str(round(leaderdf.iloc[3]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 70, 120, 100)'}),
                                dbc.ListGroupItem('3 - ' + str(leaderdf.iloc[2]['Name']) + ' : ' + str(round(leaderdf.iloc[2]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 80, 130, 100)'}),
                                dbc.ListGroupItem('4 - ' + str(leaderdf.iloc[1]['Name']) + ' : ' + str(round(leaderdf.iloc[1]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 90, 140, 100)'}),
                                dbc.ListGroupItem('5 - ' + str(leaderdf.iloc[0]['Name']) + ' : ' + str(round(leaderdf.iloc[0]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 100, 150, 100)'}),
                                dbc.ListGroupItem("* as of " +  str(date) + ' (opening prices)', style={'fontSize': '13px', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'padding-top':'0rem'}),
                                ]),
                            ], style = {'margin-left':30, 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black'})
                    ], style = {'padding-top': '1rem', 'margin-left': 30, 'width': 450}),
                ], className = 'row', style = {'margin-left':0})
            ),
        
        html.Br(),
        html.H5('Industry Distribution', style = {'color': 'orange'}),
        html.Label('Click on the labels in the legends to toggle the visibility. Click the ETF label to view the distribution of the stocks alone.', style = {'font-style': 'italic'}),      
        dcc.Loading(type = 'dot', children =
            html.Div([
                dcc.Graph(id='industryChart', figure={'layout' : {'height': 500}})
                ], style = {'margin-left':0, 'width': '60%'}),
            )
            ], style = {'margin-top': 25})
    return layout

def tab2():
    layout = html.Div([
        html.H5('Comparison of stock/ETF growth', style = {'color': 'orange'}),
        html.Label('Add more names to the selection to view the comparison in growth', style = {'font-style': 'italic'}),      
        html.Br(),
        dcc.Dropdown(
                        id='compDropDown', 
                        multi=True, 
                        # value=comparisonList,
                        options=[{'label': x, 'value': x} for x in sorted(inddf['Name'].unique())]
                    ),
        html.Br(),
        dbc.Button('Select All', id='btn-nclicks-1', color = 'info', outline=True, n_clicks=0, size="sm", className="mr-1"),
        dbc.Button('Deselect All', id='btn-nclicks-2', color = 'warning', outline=True, n_clicks=0, size="sm", className="mr-1"),
        html.Br(),
        dcc.Loading(type = 'dot', children =
            dcc.Graph(id='compLineChart', figure={})
            ),
        html.Br(),
        ], style={'margin-left':0, 'margin-top':25})
    return layout

def tab3():
    layout = html.Div([
        html.Br(),
        html.H5('Leaderboard', style = {'color': 'orange'}),
        html.Label('As of date : ' + str(date) , style = {'font-style': 'italic'}),
        html.Br(),
        html.Div([
            dt.DataTable(
                id='leaderTable',
                data = leaderboard.to_dict('records'),
                columns = columns,
                style_cell={'textAlign': 'center',
                            'backgroundColor': 'rgba(0, 0, 0, 0)'
                            }, 
                style_data={'border': '1px solid black'},
                style_header={
                    'backgroundColor': 'rgb(0, 49, 82)',
                    'fontWeight': 'bold',
                    'border': '1px solid black'
                })
            ],style={"width": "60%", 'margin-left':0}),
        html.Br(),
        ])
    return layout
    
def tab4():
    layout = html.Div([
        html.Br(),
        html.Div([
            html.Label(["Select the name",
                dcc.Dropdown(
                                id='indDropDown', 
                                multi=False, 
                                value="",
                                options=[{'label': x, 'value': x} for x in sorted(inddf['Name'].unique())]
                            ),
            ],style={"width": "20%"}),
            html.Label(["Select the stock", dcc.Dropdown(id='stockDropDown', multi=False, value='')],style = {"width": "10%", 'margin-left':10}),
            ],className = 'rows'),
        html.Br(),
        html.H5('Time series plot', style = {'color': 'orange'}),
        html.Label('Click on the legend to toggle the visibility of lines', style = {'font-style': 'italic'}),
        dcc.Loading(type = 'dot', children =
            html.Div([dcc.Graph(id='stockChart', figure = {"layout": {"height": 600}})], style={'margin-left':0}),
            ),
        html.Br(),
        html.H5('Ledger', style = {'color': 'orange'}),
        html.Div([ 
            dt.DataTable(
                id='table',
                style_cell={'textAlign': 'center',
                            'backgroundColor': 'rgba(0, 0, 0, 0)'
                            }, 
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'center'
                    } for c in ['Date', 'Region']
                ],
                style_data={'border': '1px solid black'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Status} eq Y'},
                        # 'backgroundColor': 'rgb(80, 80, 80)',
                        'color' : 'orange'
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(0, 49, 82)',
                    'fontWeight': 'bold',
                    'border': '1px solid black'
                }), 
        ], style={"width": "80%", 'margin-left':0, 'margin-top':0, 'display': 'inline-block'}),
        html.Br(),
        html.Br()
        ])
    return layout
    


@app.callback([Output('stockDropDown', 'options'),
                Output('stockDropDown', 'value')],
                Input('indDropDown', 'value')
)
def update_date_dropdown(name):
    if name == '':
        val = ''
    elif len(historydf[historydf['Name']==name]['Ticker'].unique())==1:
        val = historydf[historydf['Name']==name]['Ticker'].unique()[0]
    else:
        val = historydf[historydf['Name']==name]['Ticker'].unique()
        
    return [{'label': i, 'value': i} for i in livedict[name]], val


@app.callback(Output('stockChart', 'figure'),
                [Input('stockDropDown', 'value'),
                Input('indDropDown', 'value')])  
def display_value(value1, value2):
    dff = historydf[(historydf['Ticker']==value1) & (historydf['Name']==value2)]
    dff.set_index('Date',inplace=True)

    trace1 = {
    'x': dff.index,
    'open': dff.Open,
    'close': dff.Close,
    'high': dff.High,
    'low': dff.Low,
    'type': 'candlestick',
    'name': 'Candle stick plot',
    'showlegend': True}
    
    trace2 = {
    'x': dff.index,
    'y': dff.SMA20,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 1,
        'color': 'rgba(255,200,0,100)'
            },
    'name': 'SimpleMovingAverage20'}
    
    trace3 = {
    'x': dff.index,
    'y': dff.SMA50,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 1,
        'color': 'rgba(10,170,100,100)'
            },
    'name': 'SimpleMovingAverage50'}
    
    trace4 = {
    'x': dff.index,
    'y': dff['PriceBeforeInvestment'],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'rgba(16,129,181,100)'
            },
    'name': 'PriceBeforeInvestment'}
    
    trace5 = {
    'x': dff.index,
    'y': dff['PriceAfterInvestment'],
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'red'
            },
    'name': 'PriceBeforeInvestment'}
    
    data = [trace1, trace2, trace3, trace4, trace5]
    
    layout = dict(
        yaxis= dict(fixedrange = False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin = dict(b=0, l = 0, t =30),
        #font=dict(color="red"),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                        label='YTD',
                        step='year',
                        stepmode='todate'),
                    dict(count=1,
                        label='1y',
                        step='year',
                        stepmode='backward'),
                    dict(step='all')
                ])
            ),
        rangeslider=dict(
            visible = True,
            yaxis = dict(
                rangemode='auto'
                ),
            ),
        type='date',
        
        )
    )
    
    fig = go.Figure(data=data, layout=layout )
    fig.update_xaxes(color='white',rangeslider_bgcolor = '#404040', fixedrange = False, showgrid=True, zeroline=False, linewidth=2, linecolor='gray', gridcolor='rgb(55,55,55)', mirror=True)
    fig.update_yaxes(color='white',fixedrange = False, showgrid=True, zeroline=False, linewidth=2, linecolor='gray', gridcolor='rgb(55,55,55)', mirror=True, scaleanchor = "x", scaleratio = 1)
    fig.update_layout(legend=dict(font=dict(color='white')), title=dict(font=dict(color='orange')))
    return fig

@app.callback(Output('compDropDown', 'value'),
              Input('btn-nclicks-1', 'n_clicks'),
              Input('btn-nclicks-2', 'n_clicks'))
def displayClick(btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn-nclicks-1' in changed_id:
        comparisonList = live['Name'].unique()
    elif 'btn-nclicks-2' in changed_id:
        comparisonList = ['']
    else:
        comparisonList = leaderdf['Name'].unique()
    return comparisonList


@app.callback(  [Output('table', 'data'),
                Output('table', 'columns')],
                Input('indDropDown', 'value'))
def update_rows(value):
    dff = ledger[ledger['Name'] == value]
    dff = dff[['Date','Ticker Name', 'Exchange', 'Quantity', 'Cash', 'Status', 'Industry', 'Instrument' ]]
    columns = [{"name": i, "id": i} for i in dff.columns]
    return dff.to_dict('records'), columns



@app.callback(Output('totLineChart', 'figure'),
                Input('tabs-styled-with-inline', 'value'))  
def display_value(value):
    fig = px.line(finaldf, x='Date', y='Growth', color='Name', template='plotly_dark').update_layout(
                                   {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'
                                    }).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white", 
                                    
                                )
    return fig


@app.callback(Output('industryChart', 'figure'),
                Input('tabs-styled-with-inline', 'value'))  
def display_value(value):
    fig = px.pie(industrydf, values='Count', names='Industry', template='plotly_dark').update_layout(
                                   {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white"
                                )
    return fig


@app.callback(Output('leaderBarChart', 'figure'),
                Input('tabs-styled-with-inline', 'value'))  
def display_value(value):
    fig = px.bar(leaderdf, x=["Stocks/ETFs", "Cash"], y='Name', orientation = 'h', template='plotly_dark', hover_data=["Total"]).update_layout(
                                   {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white", 
                                ).update_traces(textposition='outside')
    return fig

@app.callback(  Output('compLineChart', 'figure'),
                Input('compDropDown', 'value'))
def display_value(value):
    dff = inddf[inddf['Name'].isin(value)]
    fig = px.line(dff, x='Date', y='Total', color='Name', template='plotly_dark').update_layout(
                                {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                'paper_bgcolor': 'rgba(0, 0, 0, 0)'}).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white"
                                )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_ui=False,dev_tools_props_check=False)
