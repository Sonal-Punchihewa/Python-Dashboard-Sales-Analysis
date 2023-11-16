#!/usr/bin/env python
# coding: utf-8

# In[10]:


import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
from dash.dependencies import Input, Output

# import dataset
df = pd.read_excel(r"/Users/sonalpunchihewa/Downloads/Globalstore.xlsx")
data = df.groupby('Category')[['Sales', 'Profit', 'Quantity', 'Discount']].sum().reset_index()

df['Order Date'] = pd.to_datetime(df['Order Date'])
tabstyle = {
    'backgroundColor': '#191970',  # Background color for tabs
    'color': '#ffffff',  # Text color for tabs
}

name = "_main_"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

# Create tabs
app.layout = html.Div([
    html.H1("Trend Analysis on a Global Store"),

    dcc.Tabs([
        dcc.Tab(label='Line Chart', children=[
            html.H2('Line Chart'),
            # Date range picker
            dcc.DatePickerRange(
                id='line-chart-date-picker',
                display_format='DD/MM/YYYY',
                min_date_allowed=min(df['Order Date']),
                max_date_allowed=max(df['Order Date']),
                initial_visible_month=max(df['Order Date']),
                start_date=min(df['Order Date']),
                end_date=max(df['Order Date'])
            ),
            # Dropdowns
            dcc.Dropdown(
                id='line-chart-dropdown',
                options=[{'label': col, 'value': col} for col in ['Sales', 'Profit', 'Quantity', 'Discount']],
                value='Sales',
                multi=False,
                style={'color': 'black'}     # Allow multiple selection
            ),

            # Line chart
            dcc.Graph(id='line-chart')
        ],style=tabstyle),

        dcc.Tab(label='Scatter Plot', children=[
            html.H2('Scatter Plot'),
            # Radio button
            dcc.RadioItems(
                id='scatter-plot-radio',
                options=[{'label': col, 'value': col} for col in ['Sales', 'Profit', 'Quantity', 'Discount']],
                value='Sales'  # Initial selection
            ),
            # Scatter plot
            dcc.Graph(id='scatter-plot')
        ],style=tabstyle),

        dcc.Tab(label='Interactive Charts', children=[
            html.H2('Interactive Charts'),

            html.Div([
                # Chart 1
                dcc.Graph(
                    id='chart1',
                    figure=px.bar(data, x='Category', y='Profit', color='Category')
                ),
                # Chart 2
                dcc.Graph(
                    id='chart2',
                    figure=px.scatter(df, x='Sales', y='Profit', color=df['Category'])
                )
            ])
        ],style=tabstyle),

        dcc.Tab(label='Custom Graph', children=[
            html.H2('Custom Graph'),
            # Box plot
            dcc.Dropdown(
                    id='custom-graph-country-dropdown',
                    options=[{'label': country, 'value': country} for country in df['Country'].unique()],
                    multi=False,
                    value='United States',
                    style={'color': 'black'}     # Initially, no country selected
            ),

# Create the pie chart for displaying sales by category
            dcc.Graph(
                id='custom-graph-pie-chart',
            ),
            dcc.Graph(
                id='custom-graph-line-chart',
            )
        ],style=tabstyle)
    ]),

    # HTML
    html.Footer(
        'Created by: Sonal Punchihewa (Index: COHNDDS231F-002)',
        style={'position': 'fixed', 'bottom': '0', 'left': '0', 'width': '100%', 'background-color': '#1a1a1a','color': '#ffffff',
               'padding': '10px'}
    )
])


# Callback line chart
@app.callback(
    dash.dependencies.Output('line-chart', 'figure'),
    dash.dependencies.Input('line-chart-date-picker', 'start_date'),
    dash.dependencies.Input('line-chart-date-picker', 'end_date'),
    dash.dependencies.Input('line-chart-dropdown', 'value'))

def update_line_chart(start_date, end_date, selected_vars):
    # Filter the dataset based on the selected date range and variables
    filtered_df = df[(df['Order Date'] >= start_date) & (df['Order Date'] <= end_date)]
    variable_data = filtered_df.groupby('Order Date')[selected_vars].sum().reset_index()
    # Create the line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=variable_data['Order Date'], y=variable_data[selected_vars], mode='lines',line=dict(color='red')))

    # Update the layout
    fig.update_layout(title='Line Chart', xaxis_title='Order Date', yaxis_title=selected_vars)

    return fig

# Callback scatter plot
@app.callback(
    dash.dependencies.Output('scatter-plot', 'figure'),
    dash.dependencies.Input('scatter-plot-radio', 'value'))
def update_scatter_plot(selected_var):
    # correlation
    correlation = df[['Sales', selected_var]].corr().iloc[0, 1]

    # Update the scatter plot
    fig = px.scatter(df, x='Sales', y=selected_var, title=f'Correlation: {correlation:.2f}')
    fig.update_traces(marker=dict(color='red')) 

    return fig


# Callback to update the scatter plot based on the selected bar in the bar graph
@app.callback(
    dash.dependencies.Output('chart2', 'figure'),
    dash.dependencies.Input('chart1', 'clickData'))
def update_scatter_plot_with_click(click_data):
    if click_data is None:
        # If no data is clicked, show the original scatter plot
        fig = px.scatter(df, x='Sales', y='Profit', title='Sales vs Profit',
                         labels={'Sales': 'Sales', 'Profit': 'Profit'})
    else:
        # Retrieve the selected category from the clicked data
        selected_category = click_data['points'][0]['x']

        # Filter the dataset based on the selected category
        filtered_df = df[df['Category'] == selected_category]

        # Create the updated scatter plot
        fig = px.scatter(filtered_df, x='Sales', y='Profit', color='Category',
                         title=f'Sales vs Profit for {selected_category}',
                         labels={'Sales': 'Sales', 'Profit': 'Profit'})
        fig.update_traces(marker=dict(color='red'))

    return fig

@app.callback(
    dash.dependencies.Output('custom-graph-pie-chart', 'figure'),
    dash.dependencies.Input('custom-graph-country-dropdown', 'value')
)
def update_pie_chart(selected_country):
    if selected_country is None:
        # If no country is selected, show all sales by country
        country_data = df.groupby('Country')['Sales'].sum().reset_index()
        fig = px.pie(country_data, names='Country', values='Sales', title='Sales by Country')
    else:
        # If a country is selected, show sales by category for that country
        country_data = df[df['Country'] == selected_country]
        category_sales = country_data.groupby('Category')['Sales'].sum().reset_index()
        fig = px.pie(category_sales, names='Category', values='Sales', title=f'Sales by Category in {selected_country}')

    return fig

@app.callback(
    dash.dependencies.Output('custom-graph-line-chart', 'figure'),
    dash.dependencies.Input('custom-graph-country-dropdown', 'value')
)
def update_line_chart(selected_country):
    if selected_country is None:
        # If no country is selected, do not display the line chart
        return {'data': [], 'layout': {}}

    # Filter the dataset for the selected country
    country_data = df[df['Country'] == selected_country]

    # Group by order date and calculate sales
    order_date_sales = country_data.groupby('Order Date')['Sales'].sum().reset_index()

    # Create the line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=order_date_sales['Order Date'], y=order_date_sales['Sales'], mode='lines'))

    # Update the layout
    fig.update_layout(title=f'Sales by Order Date in {selected_country}', xaxis_title='Order Date', yaxis_title='Sales')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True,port=9092)

