import plotly.plotly as py
import plotly

dic1 = dict(
    type = 'scattergeo',
    locationmode = 'USA-states',
    lon = 42.7,
    lat = -84.48,
    text = 'test',
    mode = 'markers',
    marker = dict(
        size = 10,
        symbol = 'star',
        color = 'red'
    ))

data = [dic1]
#min_lat = 10000
#max_lat = -10000
#min_lon = 10000
#max_lon = -10000

#lat_vals = lat
#lon_vals = lng
#for str_v in lat_vals:
#v = float(str_v)
#if v < min_lat:
    #min_lat = v
#if v > max_lat:
    #max_lat = v
#for str_v in lon_vals:
#v = float(str_v)
#if v < min_lon:
    #min_lon = v
#if v > max_lon:
    #max_lon = v

center_lat = .07
center_lon = .05

max_range = .1
padding = .10
lat_axis = [42.68 - padding,  42.75 + padding]
lon_axis = [-84.5 - padding, -84.4 + padding]

layout = dict(
    geo = dict(
        scope='usa',
        projection=dict( type='albers usa' ),
        showland = True,
        landcolor = "rgb(250, 250, 210)", #yellow
        subunitcolor = "rgb(0, 0, 0)", #black
        countrycolor = "rgb(0, 0, 0)",
        lataxis = {'range': lat_axis},
        lonaxis = {'range': lon_axis},
        center = {'lat': center_lat, 'lon': center_lon },
        countrywidth = .5,
        subunitwidth = .5
    ),
)

fig = dict(data=data, layout=layout)

print(fig)

py.plot(fig, validate=False, filename='msu_building')

