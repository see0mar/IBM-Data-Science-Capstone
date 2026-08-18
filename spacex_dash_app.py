# Import required libraries
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown input component
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] +
                         [{'label': s, 'value': s} for s in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True),
    html.Br(),

    # TASK 3: Payload range slider input component
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2000)},
                    value=[0, 10000]),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback to render success-pie-chart based on selected site
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Summing the 0/1 class column per site = total successful launches per site
        fig = px.pie(spacex_df, values='class', names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = site_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['outcome'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='count', names='outcome',
                     title=f'Success vs Failure Launches for {entered_site}')
    return fig

# TASK 4: Callback to render success-payload-scatter-chart (site + payload range)
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    mask = (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & \
           (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    filtered_df = spacex_df[mask]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs. Launch Success (All Sites)')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Launch Success ({entered_site})')
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
    