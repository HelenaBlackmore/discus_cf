# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 11:40:15 2021

@author: Helena
"""

 
import dash
import dash_core_components as dcc
import dash_html_components as html


import plotly.express as px
import pandas as pd




receipt = pd.read_csv("receipt.csv") #reads the csv receipt
receipt = receipt[receipt.columns[[0,1,2,3,7,8,9]]]
receipt = receipt.dropna()

#%%
# remove £ sign
receipt.price = receipt.price.str.split('£').str.get(-1)

receipt.co2_item = pd.to_numeric(receipt.co2_item)


#%%

# add a classification variable to visualise high, medium or low impact
low = 3
low_std = 5

medium = 10  # these values are arbitrary, morer research needed 
medium_std = 12             # potentially these could be set by the user orrealtive to average item in the shopping/ or relative to total

receipt.loc[receipt['co2_item'] <= low, 'impact'] = 'low'
receipt.loc[receipt['co2_item'] > medium, 'impact'] = 'high'
receipt.loc[receipt['co2_item'] > low, 'impact'] = 'medium'

receipt.loc[receipt['co2_kg'] <= low, 'impact_std'] = 'low'
receipt.loc[receipt['co2_kg'] > medium, 'impact_std'] = 'high'
receipt.loc[receipt['co2_kg'] > low, 'impact_std'] = 'medium'

#%%

#  order items by impact 
  #  primarily impact by item, if items have identical impact, the one that has larger impact per kg/l will be displayed first

receipt_item = receipt.sort_values(by=['co2_item', 'co2_kg'], ascending=True)
  #might have to remove once I have one long dataset 

# order items by impact per kg
receipt_std = receipt.sort_values(by=['co2_kg'], ascending=True)

total = round(sum(receipt_item.co2_item),1)

distance_miles = round((total * 0.411),0)           # very rough estimate
distance_km = round((distance_miles * 1.60934),0)   # this is fine, accuarte enough


to_swap = receipt_std[receipt_std.co2_kg==max(receipt_std.co2_kg)]
substitute= to_swap.iloc[0]['item']

swap = "**something else**"   # at the moment manual, later will be based on output from SQL query (matching protein content)

cf_dif = 30   # cf_dif = (1- swap/to_swap)*100
#%%

fig = px.bar(receipt_item, 
             x='co2_item',
             y='item',
             orientation = 'h', 
             color = 'impact', 
             height=800,
             hover_name="item",
             hover_data = {"impact"},
             labels={ 
                  "co2_item": "co\u2082 equivalent (kg)", "item":""},
             color_discrete_map={ 
                "low": "green", "medium": "orange", "high" : "red"},
             template="simple_white")

fig.update_layout( # customize font and legend orientation & position
    showlegend = False,
    title= { "text": "Carbon Footprint per item", "x" : 0.5, "xanchor": "center", "yanchor": "middle", "font" : {"size" : 25}  }
     )



fig.update_xaxes(visible = False )
fig.update_yaxes(ticks=""  )


#%%

# plot based on standardised impact ( ie. disregards weight of item)


fig_std = px.bar(receipt_std, 
             x='co2_kg',
             y='item',
             orientation = 'h', 
             color = 'impact_std', 
             height=800,
             hover_name="item",
             hover_data = {"impact_std"},
             labels={ 
                  "co2_item": "co\u2082 equivalent (kg)", "item":""},
             color_discrete_map={ 
                "low": "green", "medium": "orange", "high" : "red"},
             template="simple_white")

fig_std.update_layout( # customize font and legend orientation & position
    showlegend = False,
    title= { "text": "Carbon Footprint per kg of product", "x" : 0.5, "xanchor": "center", "yanchor": "middle", "font" : {"size" : 25}  }
     )

fig_std.update_xaxes(visible = False )
fig_std.update_yaxes(ticks=""  )


#%% Dashboard

external_stylesheets = [
    {   "href": "https://fonts.googleapis.com/css2?family=Zen+Loop&display=swap",
        "rel": "stylesheet",
    },
] #this did not work, so font was set to 'Zen loop' in the external css


app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
app.title = "CO\u2082 receipts"


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="My CO\u2082 receipt", className="header-title"
                ),
                html.P(
                    children="See the carbon footprint of your shopping "
                    "and how to lower your impact!\n"
                    "To learn more about how carbon footprint is measured and "
                    "how different foods rank, check out:",
                    className="header-description",
                ),
                html.A(children = "Our world in data: Food choice", 
                       href = "https://ourworldindata.org/food-choice-vs-eating-local",
                       className = "link-moreinfo"
                        ),
            ],
            className="header",
        ),
             html.Div(children=[
                        html.Div(children=[
                                html.Div(children="Sort items in my shop by... ", 
                                         className="menu-title"),
                                dcc.Dropdown(id="graph",
                                             options=[
                        {"label": "impact per item", "value": "item"},
                        {"label":"impact per kg", "value": "kg"},
                    ],
                                            value="item",
                                            clearable=False,
                                            className="dropdown",
                ),
                                html.Img(alt = "co2 cloud", 
                                         src ="assets/co2_cloud.png",
                                         className="icon-cloud"),
                                html.P(children = "The food in your shopping was responsible " 
                                       "for greenhouse gases emissions " 
                                       "equivalent to {} kg of CO\u2082".format(total), 
                                       className = "total-cf"),
                                html.Img(alt = "car exhaust", 
                                         src = "assets/emission_car.png",
                                         className = "icon-car"),
                                html.P(children = " Similar amount of CO\u2082 would be emitted by "
                                       "an average car driving {} miles / {} km".format(distance_miles, distance_km),
                                       className = "drive-cf"),
                                html.Img(alt = "holding planet",
                                         src = "assets/planet.png",
                                         className = "icon-planet"),
                                html.P(children = '''You bought {}. Do you know that {} has 
                                                   a similar protein content but {} % lower carbon footprint?'''.format(substitute,swap,cf_dif),
                                       className = "swap")
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                figure= fig, # co2 equivalents per item
                className="card",
                                        ),
                            ),
                            
                html.Div(
                    children = dcc.Graph(
                figure = fig_std, # co2 equivalents per kg of product 
                className = "card",
                ),
            ),
                
                
            ],
            className="wrapper",
        ),
        html.Div(
                children = html.Footer(
                  children = [
                    html.H4(children = ["I WANT TO KNOW MORE", "",
                            html.A(children = "impact of methane\n", 
                           href = "https://ourworldindata.org/carbon-footprint-food-methane",
                           className = "link-resources"),
                            html.A(children = "environmental impact of food production\n",
                           href = "https://ourworldindata.org/environmental-impacts-of-food",
                           className = "link-resources"),
                            html.A(children = "BBC: climate change food calculator\n", 
                           href = "https://www.bbc.co.uk/news/science-environment-46459714",
                           className = "link-resources"),
                            html.A(children = "carbon footprint factsheet", 
                           href = "https://css.umich.edu/factsheets/carbon-footprint-factsheet",
                           className = "link-resources")],
                            className = "h4"),          
                    html.H4(children = [ "DATA", "",
                            html.A(children = "food carbon footprint of food comodities: article", 
                           href = "https://pubmed.ncbi.nlm.nih.gov/33963181/", 
                           className = "link-resources"),
                            html.A(children = "carbon footprint of food comodities: data",
                           href = "https://figshare.com/articles/dataset/SU-EATABLE_LIFE_a_comprehensive_database_of_carbon_and_water_footprints_of_food_commodities/13271111",
                           className = "link-resources"),
                            html.A(children = "nutritional information",
                           href = "https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid",
                           className = "link-resources")
                                        ],
                            className = "h4"),
                    html.H4(children = ["ICONS","",
                            html.A(children = "Icons made by Dinosoft Labs and Freepik from Flaticon.com", 
                           href = "https://www.flaticon.com/",
                           className = "link-resources")],
                            className = "h4"),
                    ],
                            className = "footer"
                    ),
                 

                                ),
                 
        
                
                                ]
            ) ])    
   
                    
            
            
if __name__ == "__main__":
    app.run_server(debug=True)
    
