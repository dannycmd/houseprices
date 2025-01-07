from pathlib import Path
import os
import json
import pandas as pd
from ipyleaflet import Map, Choropleth
from shiny import App, Inputs, Outputs, Session, ui, reactive, render
from shinywidgets import output_widget, render_widget
from branca.colormap import linear

### Load data
appDir = Path(os.path.abspath(''))
# used https://mapshaper.org/ to simplify the GeoJSON file, reducing its size using the Visvalingam / weighted area method with a 1% zoom level
with open(appDir / 'OutcodeCoordinates_compressed.json', 'r') as f:
    outcodeCoordinates = json.load(f)
outcodes = [i['id'] for i in outcodeCoordinates['features']]
summary = pd.read_csv(appDir / 'summary.csv', encoding='utf-8', delimiter=',')
summary = summary[(~summary['Outcode'].isnull()) & (summary['Outcode'].isin(outcodes))]
summary = summary.rename(columns={"range_": "range"})
yearBins = list(summary['YearBin'].unique())

# Nest Python functions to build an HTML interface
app_ui = ui.page_fillable( 
    # Layout the UI with Layout Functions
    # Add Inputs with ui.input_*() functions 
    # Add Outputs with ui.output_*() functions
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_checkbox_group('yearBin', "Time Period", yearBins),
            ui.input_select('statistic', "House Price Summary Statistic", ['mean', 'median', 'min', 'max', 'IQR', 'range', 'skew'], selected='median', multiple=False),
            ui.input_switch("switch", "Compare Summary Statistic between Time Periods", False)
        ),
        ui.card(
            ui.output_image("image", height='10px'),
            output_widget("map", fill=True),
            full_screen=True,
            fill=True
        ),
        ui.card_footer("Contains HM Land Registry data © Crown copyright and database right 2021. This data is licensed under the Open Government Licence v3.0."),
        full_screen=True
    ),
    title="House Prices Visualisation"
)

# Define server
def server(input: Inputs, output: Outputs, session: Session):
    # add colour map image
    @render.image
    def image():
        img = {"src": appDir / "ColourMap.jpg", "width": "300px"}  
        return img

    # function to filter the summary dataset and return a lookup dictionary with a key for each Outcode
    @reactive.calc
    def createChoroData():

        # select all time periods if none are selected
        if input.yearBin() == tuple():
            filter = yearBins
        else:
            filter = list(input.yearBin())

        # logic for comparing summary stastics between time periods
        if input.switch():
            minYearBin = filter[0]
            maxYearBin = filter[-1]
            dfMin = summary[summary['YearBin'] == minYearBin][['Outcode', input.statistic()]]
            dfMax = summary[summary['YearBin'] == maxYearBin][['Outcode', input.statistic()]]
            df = pd.merge(dfMin, dfMax, how="inner", on="Outcode")
            df['diff'] = df[input.statistic() + '_y'] - df[input.statistic() + '_x']
            df = df.set_index('Outcode')
            df['decile'] = pd.qcut(df['diff'], 10, labels=False)
            return df['decile'].to_dict()                
        # if not comparing time periods then just show summary statistic
        else:
            df = summary[summary['YearBin'].isin(filter)].set_index('Outcode')
            df['decile'] = pd.qcut(df[input.statistic()], 10, labels=False)
            return df['decile'].to_dict()

    ### For each output, define a function that generates the output
    @render_widget  
    def map():
        # create a Map object and add a Choropleth layer to it
        m = Map(center=(54.00366, -2.547855), zoom=5.5, zoom_snap=0.2, zoom_delta=0.2)

        try:
            layer = Choropleth(
                    geo_data=outcodeCoordinates,
                    choro_data=createChoroData(),
                    key_on='id',
                    colormap=linear.viridis,
                    border_color='black',
                    style={'fillOpacity': 0.8, 'dashArray': '5, 5'}
                )
        except:
            raise IndexError("Must select more than one time period if comparing summary statistic between time periods.")

        m.add(layer)

        return m

# Call App() to combine app_ui and server() into an interactive app
app = App(app_ui, server)