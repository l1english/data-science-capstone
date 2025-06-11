# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                    # TASK 1: Launch site dropdown list
    html.Div(dcc.Dropdown(id='site-dropdown',
                          options=[
                              {'label': 'All Sites', 'value': 'All Sites'},
                              {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                              {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                              {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                              {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                          ],
                          value='All Sites',  # Default value
                          placeholder="Select a Launch Site",
                          searchable=True)),  
    
    html.Br(),
    
    # TASK 2: Pie chart for success count
    html.Div([
        html.Div(dcc.Graph(id='success-pie-chart')),  # Success pie chart
        html.Div(dcc.Graph(id='failure-pie-chart'))   # Failure pie chart
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Payload range slider
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload,
                    max=max_payload,
                    step=1000,
                    marks={0: '0',
                           max_payload // 2: str(max_payload // 2),
                           max_payload: str(max_payload)},
                    value=[min_payload, max_payload]),  # Missing comma after this line
    
    # TASK 4: Scatter chart to show correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback to update pie chart based on launch site selection
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'All Sites':
        # Filter the dataframe for all sites
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(names=['Success', 'Failure'], values=[success_count, failure_count],
                     title='Total Successful vs. Failed Launches By Site')
    else:
        # Filter the dataframe for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(names=['Success', 'Failure'], values=[success_count, failure_count],
                     title=f'Success vs. Failure for {entered_site}')
    
    return fig

# TASK 4: Callback to update scatter chart based on payload and site selection
[Output('success-pie-chart', 'figure'),
     Output('failure-pie-chart', 'figure')],
    [Input('site-dropdown', 'value')]
)
def update_pie_charts(selected_site):
    filtered_df = spacex_df
    
    # If "All Sites" is selected, show success and failure across all sites
    if selected_site == 'All Sites':
        # Success counts per site
        success_counts = filtered_df.groupby('Launch Site')['class'].apply(lambda x: (x == 1).sum()).reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']
        
        # Failure counts per site
        failure_counts = filtered_df.groupby('Launch Site')['class'].apply(lambda x: (x == 0).sum()).reset_index()
        failure_counts.columns = ['Launch Site', 'Failure Count']
        
        # Pie chart for Success Rate across all sites
        success_fig = px.pie(success_counts, names='Launch Site', values='Success Count', 
                             title='Success Rate By Site')
        
        # Pie chart for Failure Rate across all sites
        failure_fig = px.pie(failure_counts, names='Launch Site', values='Failure Count', 
                             title='Failure Rate By Site')
        
        return success_fig, failure_fig
        
     else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(names=['Success', 'Failure'], values=[success_count, failure_count],
                     title=f'Success vs. Failure for {entered_site}')
        
        return fig

                             
    # Filter by payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Create scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class',
                     labels={'class': 'Launch Success (1 = Success, 0 = Failure)'},
                     title=f'Payload vs. Success for {entered_site} (Payload Range: {payload_range[0]} - {payload_range[1]})')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
