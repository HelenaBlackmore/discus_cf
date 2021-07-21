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

receipt = receipt.sort_values(by=['co2_item', 'co2_kg'], ascending=True)
# order items by impact per kg
receipt_std = receipt.sort_values(by=['co2_kg'], ascending=True)


#%%

fig = px.bar(receipt, 
             x='co2_item',
             y='item',
             orientation = 'h', 
             color = 'impact', 
             height=500,
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
             height=500,
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
] #this did not work, so font was set to 'Zen loop' in the css


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
                    "what foods to avoid, check out:",
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
                                html.Div(children="type of visualisation", 
                                         className="menu-title"),
                                dcc.Dropdown(id="graph",
                                             options=[
                        {"label": "impact per item", "value": "item"},
                        {"label":"impact per kg ofproduct", "value": "kg"},
                    ],
                                            value="impact per item",
                                            clearable=False,
                                            className="dropdown",
                ),
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
    ],
                )
                                ]
            )      
                    
            
            
if __name__ == "__main__":
    app.run_server(debug=True)