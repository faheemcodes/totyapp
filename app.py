import os
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

#VALID_USERNAME_PASSWORD_PAIRS = {
#    'faheemkk': 'pass'
#}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server
#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)

#currentPath = os.getcwd()
#path = r'C:/Users/FaheemKK/Desktop/Toty/totyapp/assets/ledgerBackup/'
#os.chdir(path)
#files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
#ledgerFile = files[-1]
#os.chdir(currentPath)

today = date(2021,1,9)
start_date = date(2021,1,4)
fileName = 'assets/Trade of the year_Final.xlsm'

totdf = pd.read_csv('assets/TotalPortfolio_' + str(today) + '.csv')
cppdf = pd.read_csv('assets/totalFund.csv')
cppdf = cppdf[cppdf['Date'] >= str(start_date)]
totdf['Name'] = 'DAA Portfolio'
totPercent = round((totdf.iloc[-1]['totalSum']-totdf.iloc[-2]['totalSum'])/totdf.iloc[-2]['totalSum']*100,2)
cppPercent = round((cppdf.iloc[-1]['totalSum']-cppdf.iloc[-2]['totalSum'])/cppdf.iloc[-2]['totalSum']*100,2)
totGrowth = round((totdf.iloc[-1]['Growth']-1)*100,2)
cppGrowth = round((cppdf.iloc[-1]['totalSum']/cppdf.iloc[0]['totalSum']-1)*100,2)

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

cppdf['Name'] = 'CPP Portfolio'
cppdf['stockSum'] = ''
cppdf['cashSum'] = ''
base_price = cppdf.iloc[0]['totalSum']
cppdf['Growth'] = cppdf['totalSum']/base_price
totdf = pd.concat([totdf, cppdf])


inddf = pd.read_csv('assets/IndividualPortfolio_' + str(today) + '.csv')
date = inddf['Date'].unique().max()
inddf.columns = ['Name', 'Stocks', 'Cash', 'Total', 'Date']

live = pd.read_excel(fileName, sheet_name = 'Live', skiprows = 3, converters= {'Date': pd.to_datetime})
ledger = pd.read_excel(fileName, sheet_name = 'Ledger', skiprows = 4, converters= {'Date': pd.to_datetime})
#live = ledger[ledger['Status']=='Y']
industrydf = live.groupby('Industry').size().reset_index()
industrydf.columns = ['Industry', 'Count']
leaderdf = inddf[inddf['Date']== str(date)].sort_values(by=['Total'], ascending=False)[:5].sort_values(by=['Total'], ascending=True)
leaderdf.columns = ['Name', 'Stocks', 'Cash', 'Total', 'Date']

tabs_styles = {
    'height': '30px',
    'width' : '30%'
}
tab_style = {
    'padding': '1.2px',
    'backgroundColor': '#444444',
    'fontColor': 'black',
    'border': '0px solid grey'
}
tab_selected_style = {
    'backgroundColor': '#296d98',
    'color': 'white',
    'padding': '1.2px',
    'border': '0px solid grey'
}


app.layout = html.Div([
    html.Div(style={'height':75, 'margin-left':400, 'margin-right':400}, children = [
        html.Br(),
        html.H3('Trade of the year !!!!', style={"textAlign": "center", 'fontColor': 'white', 'margin-top':1, 'padding-top': '0rem'}),
        html.Br()
        ], className = 'rows'),

    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Main', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Comparison', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Individual', value='tab-3', style=tab_style, selected_style=tab_selected_style),
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


def tab1():
    layout = html.Div([

        html.Div([
            dcc.Graph(id='totLineChart', figure={'layout' : {'height': 420}}, style={"width": '80%'}),

            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.ListGroupItem("Daily Changes", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                        dbc.ListGroupItem("DAA Portfolio : " + str(totPercent) + "%" ,color=totColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                        dbc.ListGroupItem("CPP Total Fund : " + str(cppPercent) + "%" ,color=cppColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                    ], style={'backgroundColor': 'rgba(0, 0, 0, 0)', 'padding-top': '0rem', 'padding-left': '0rem', 'border':'0px solid black'}),
                dbc.CardBody(
                    [
                        dbc.ListGroupItem("Overall Growth", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                        dbc.ListGroupItem("DAA Portfolio : " + str(totGrowth) + '%',color=totGrowthColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                        dbc.ListGroupItem("CPP Total Fund : " + str(cppGrowth) + '%',color=cppGrowthColor, style={'fontSize': '13px', 'textAlign': 'center'}),
                        dbc.ListGroupItem("* growth from 4th Jan 2021", style={'fontSize': '13px', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'padding-top':'0rem'}),
                    ], style={'backgroundColor': 'rgba(0, 0, 0, 0)', 'padding-top': '0rem', 'padding-left': '0rem', 'border':'0px solid black'}),
                ],style={"width": "17%", 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'margin-left':30})
            ], className = 'row'),

        html.Div([
            html.Div
                ([dcc.Graph(id='leaderBarChart', figure={'layout' : {'height': 450}})], style = {'margin-left':30}),
            html.Div
                ([dbc.Card([
                        dbc.CardBody([
                            dbc.ListGroupItem("Total Amount (Stocks + Cash)", style={'color':'rgba(160, 160, 160, 100)', 'border': '0px solid black', 'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                            dbc.ListGroupItem('1 - ' + str(leaderdf.iloc[4]['Name']) + ' : ' + str(round(leaderdf.iloc[4]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 60, 110, 100)'}),
                            dbc.ListGroupItem('2 - ' + str(leaderdf.iloc[3]['Name']) + ' : ' + str(round(leaderdf.iloc[3]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 70, 120, 100)'}),
                            dbc.ListGroupItem('3 - ' + str(leaderdf.iloc[2]['Name']) + ' : ' + str(round(leaderdf.iloc[2]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 80, 130, 100)'}),
                            dbc.ListGroupItem('4 - ' + str(leaderdf.iloc[1]['Name']) + ' : ' + str(round(leaderdf.iloc[1]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 90, 140, 100)'}),
                            dbc.ListGroupItem('5 - ' + str(leaderdf.iloc[0]['Name']) + ' : ' + str(round(leaderdf.iloc[0]['Total']/1000,1)) + ' k USD' , style={'fontSize': '13px', 'fontWeight': 'bold', 'border': '0px solid black', 'backgroundColor': 'rgba(0, 100, 150, 100)'}),
                            dbc.ListGroupItem("* as of " +  str(today), style={'fontSize': '13px', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black', 'padding-top':'0rem'}),
                            ]),
                        ], style = {'margin-left':30, 'backgroundColor': 'rgba(0, 0, 0, 0)', 'border': '0px solid black'})
                ], style = {'padding-top': '4rem', 'margin-left': 30, 'width': 450}),
            ], className = 'row'),

        html.Div
                ([dcc.Graph(id='industryChart', figure={'layout' : {'height': 500}})
            ], style = {'margin-left':30, 'width': '60%'}),
            
        ])
    return layout

def tab2():
    layout = html.Div([
        html.Br(),
        dbc.Button('Select All', id='btn-nclicks-1', color = 'info', outline=True, n_clicks=0, size="sm", className="mr-1"),
        dbc.Button('Deselect All', id='btn-nclicks-2', color = 'warning', outline=True, n_clicks=0, size="sm", className="mr-1"),
        html.Br(),
        html.Br(),
        dcc.Dropdown(
                        id='compDropDown', 
                        multi=True, 
                        # value=comparisonList,
                        options=[{'label': x, 'value': x} for x in sorted(inddf['Name'].unique())]
                    ),
        dcc.Graph(id='compLineChart', figure={})
        ], style={'margin-left':40, 'margin-right':40})
    return layout

def tab3():
    layout = html.Div([
        html.Br(),
        html.Div([
            dcc.Dropdown(
                            id='indDropDown', 
                            multi=False, 
                            value="Alex Tait",
                            options=[{'label': x, 'value': x} for x in sorted(inddf['Name'].unique())]
                        ),
        ],style={"width": "20%", 'margin-left':10}),
        html.Br(),
        html.Div(id='table'),
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
                })
        ],style={"width": "50%", 'margin-left':10})
                    
        ])
    return layout

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
    # return [dt.DataTable(data=dff, columns=columns)]
    return dff.to_dict('records'), columns


@app.callback(Output('totLineChart', 'figure'),
                Input('tabs-styled-with-inline', 'value'))  
def display_value(value):
    fig = px.line(totdf, x='Date', y='Growth', color='Name', title='Growth - DAA & CPP Portfolio', template='plotly_dark').update_layout(
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
    fig = px.pie(industrydf, values='Count', names='Industry', title='Industry Distribution', template='plotly_dark').update_layout(
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
    fig = px.bar(leaderdf, x=["Stocks", "Cash"], y='Name', title='Leaderboard', orientation = 'h', template='plotly_dark', hover_data=["Total"]).update_layout(
                                   {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white"
                                ).update_traces(textposition='outside')
    return fig

@app.callback(  Output('compLineChart', 'figure'),
                Input('compDropDown', 'value'))
def display_value(value):
    dff = inddf[inddf['Name'].isin(value)]
    fig = px.line(dff, x='Date', y='Total', color='Name', title='Comparison of stock growth', template='plotly_dark').update_layout(
                                {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                'paper_bgcolor': 'rgba(0, 0, 0, 0)'}).update_layout(
                                    font_color="white",
                                    title_font_color="orange",
                                    legend_title_font_color="white"
                                )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_ui=False,dev_tools_props_check=False)
