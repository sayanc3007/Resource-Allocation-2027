import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1. LOAD THE EXCEL FILE
file_path = 'Resource Allocation snapshot 2027.xlsx'
df = pd.read_excel(file_path, sheet_name=0)

# Filter out Totals and Unallocated based on the Country Name column (now at index 2)
df = df[~df[df.columns[2]].astype(str).str.contains('Total', case=False, na=False)]
df = df[~df[df.columns[2]].astype(str).str.contains('Unallocated', case=False, na=False)]
df = df.dropna(subset=[df.columns[2]])  

# 2. EXTRACT RELEVANT COLUMNS 
country_col = df.columns[2] # Column C (Country Name) is at index 2
widget_columns = df.columns[5:19].tolist() # Resource categories from Column F to Column Q (indices 5 through 16)

# 3. CLEAN DATA
# Ensure all selected columns are numeric (converts "-" or missing values to 0)
for col in widget_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 4. INITIALIZE THE DASH APP
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("2027 Snapshot: Global Resource Distribution", style={'fontFamily': 'Arial', 'textAlign': 'center'}),
   
    html.Div([
        html.Label("Select Resource Categories to Calculate:", style={'fontWeight': 'bold'}),
        # Multi-select Checkboxes
        dcc.Checklist(
            id='resource-checkboxes',
            options=[{'label': col, 'value': col} for col in widget_columns],
            value=[widget_columns[0]],  # Select the first checkbox by default to show initial data
            inline=True,
            style={'fontFamily': 'Arial', 'padding': '15px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '8px'}
        )
    ], style={'marginBottom': '20px'}),
   
    # Choropleth Map Container
    dcc.Graph(id='choropleth-map', style={'height': '75vh'})
])

# 5. DEFINE INTERACTIVE LOGIC (Callback)
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('resource-checkboxes', 'value')
)
def update_map(selected_cols):
    # Handle empty selection
    if not selected_cols:
        return px.choropleth(title="Please select at least one resource category from the checkboxes above.")
       
    # Dynamically sum the selected columns for each country row
    df['Dynamic_Total'] = df[selected_cols].sum(axis=1)


    # Calculate max value. If everything is 0, set upper bound to 1 so '0' stays white.
    max_val = df['Dynamic_Total'].max()
    upper_bound = max_val if max_val > 0 else 1
    
    # Changed the first color to #ffffff (pure white) for zero-values
    brown_shades = ['#ffffff', '#e3d2bf', '#bf9f7d', '#966e4a', '#6e4523', '#401e05']

    fig = px.choropleth( 
        df, 
        locations=country_col, 
        locationmode='country names', 
        color='Dynamic_Total', 
        hover_name=country_col, 
        hover_data={country_col: False, 'Dynamic_Total': ':,.0f'}, 
        color_continuous_scale=brown_shades, 
        labels={'Dynamic_Total': 'Total Resources'}, 
        title="Total Resources for Selected Categories"   
    )
   
    # Layout styling for a clean world map
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showocean=True, oceancolor="LightBlue",
            showland=True, landcolor="White"
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        coloraxis_colorbar=dict(title="Total Resources")
    )
   
    return fig

# 6. RUN THE SERVER
if __name__ == '__main__':
    print("Starting dashboard... Open the provided http://127.0.0.1:8050 link in your web browser.")
    app.run(debug=True)
