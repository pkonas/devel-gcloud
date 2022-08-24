import pandas as pd
from datetime import datetime
from app import db
from bokeh.layouts import column
from bokeh.plotting import show, figure
from bokeh.models import ColumnDataSource, AjaxDataSource, DatetimeTickFormatter, NumeralTickFormatter, CustomJS, DatetimeRangeSlider, HoverTool
from bokeh.io import curdoc
from bokeh.embed import components


def livecharts():
    # setup AjaxDataSource with URL and polling interval
    source = AjaxDataSource(data_url='https://twin.svsfem.cz/api/data/lastchart',
                            polling_interval=8000, method= "GET", mode='append')
    print(source)
    tooltips = [
        ("time", "@datetime{%F %T}"),        
        ("value", "$y{0.0}"),
    ]
  
    TOOLS = "pan,box_zoom,wheel_zoom,lasso_select,save,reset"

    # use the AjaxDataSource just like a ColumnDataSource
    curdoc().theme = 'caliber'
    height = 325
    width = 1100

    p1 = figure(height=height, width=width, title="Pressure", sizing_mode="stretch_width",x_axis_type="datetime",
    y_axis_label="Pressure [Pa]", x_axis_label="Time", tools=TOOLS)
    p1.line("datetime", "pressure1", source=source, line_width=2, color="navy", legend="Pressure1")
    p1.circle("datetime", "pressure1", source=source, size=10, color="navy", fill_color="white")

    p1.line("datetime", "pressure2", source=source, line_width=2, color="firebrick", legend="Pressure2")
    p1.triangle("datetime", "pressure2", source=source, size=10, color="firebrick", fill_color="white")

    p2 = figure(height=height, width=width, title="Flow", x_axis_type="datetime", sizing_mode="stretch_width",
    y_axis_label="Flow rate [l/h]",  x_axis_label="Time", x_range=p1.x_range, tools=TOOLS)
    p2.line("datetime", "flow1", source=source, line_width=2, color="navy", legend="Flow1")
    p2.circle("datetime", "flow1", source=source, size=10, color="navy", fill_color="white")

    p2.line("datetime", "flow2", source=source, line_width=2, color="firebrick", legend="Flow2")
    p2.triangle("datetime", "flow2", source=source, size=10, color="firebrick", fill_color="white")   

    p3 = figure(height=height, width=width, title="Valve position", x_axis_type="datetime", y_range=(0, 100),
    sizing_mode="stretch_width", y_axis_label="Position [-]", x_axis_label="Time", x_range=p1.x_range,
    tools=TOOLS)
    p3.line("datetime", "valve_position", source=source, line_width=2, color="olive", legend="Valve position")
    p3.circle("datetime", "valve_position", source=source, size=10, color="olive", fill_color="white")

    p4 = figure(height=height, width=width, title="Temperature", x_axis_type="datetime",
    sizing_mode="stretch_width", y_axis_label="Temperature [°C]", x_axis_label="Time", x_range=p1.x_range,
    tools=TOOLS)
    p4.line("datetime", "temperature", source=source, line_width=2, color="orange", legend="Temperature")
    p4.circle("datetime", "temperature", source=source, size=10, color="orange", fill_color="white")

    p1.x_range.follow = "end"
    p1.x_range.follow_interval = 100
    p2.x_range.follow = "end"
    p2.x_range.follow_interval = 100
    p3.x_range.follow = "end"
    p3.x_range.follow_interval = 100
    p4.x_range.follow = "end"
    p4.x_range.follow_interval = 100
    p1.legend.location = "top_left"
    p1.legend.click_policy="hide"
    p2.legend.location = "top_left"
    p2.legend.click_policy="hide"
    p3.legend.location = "top_left"
    p4.legend.location = "top_left"
    
    p1.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime' }))
    p2.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))    
    p3.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))    
    p4.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))

    p1.yaxis.formatter = NumeralTickFormatter(format="0 a")
    # p3.xaxis.formatter=DatetimeTickFormatter(
    #     microseconds=["%H:%M:%S"],
    #     milliseconds=["%H:%M:%S"],
    #     hours=["%H:%M:%S"],
    #     days=["%H:%M:%S"],
    #     months=["%H:%M:%S"],
    #     years=["%H:%M:%S"],
    # )
    

    script, div = components(column(p3,p1,p2,p4,sizing_mode='stretch_both'))
    return script, div

def history_chart():
    sql_query = pd.read_sql("data",'sqlite:///app.db',index_col=["id"],coerce_float=False,
                            columns=["datetime","pressure1","pressure2","flow1","flow2","temperature","valve_position"],
                            parse_dates=["datetime"])
    df = pd.DataFrame(sql_query)
    source = ColumnDataSource(df)
    
    tooltips = [
        ("time", "@datetime{%F %T}"),        
        ("value", "$y{0.0}"),
    ]
    
    TOOLS = "pan,box_zoom,wheel_zoom,lasso_select,save,reset"

    # use the AjaxDataSource just like a ColumnDataSource
    curdoc().theme = 'caliber'
    height = 600
    width = 1100

    p1 = figure(height=height, width=width, title="Pressure", sizing_mode="stretch_width", x_axis_type="datetime",
    y_axis_label="Pressure [Pa]", x_axis_label="Time", tools=TOOLS)
    p1.line("datetime", "pressure1", source=source, line_width=2, color="navy", legend="Pressure1")

    p1.line("datetime", "pressure2", source=source, line_width=2, color="firebrick", legend="Pressure2")

    p2 = figure(height=height, width=width, title="Flow", x_axis_type="datetime", sizing_mode="stretch_width",
    y_axis_label="Flow rate [m3/h]",  x_axis_label="Time", x_range=p1.x_range,  tools=TOOLS)
    p2.line("datetime", "flow1", source=source, line_width=2, color="navy", legend="Flow")

    p2.line("datetime", "flow2", source=source, line_width=2, color="firebrick", legend="Flow2")

    p3 = figure(height=height, width=width, title="Valve position", x_axis_type="datetime", y_range=(0, 100),
    sizing_mode="stretch_width", y_axis_label="Position [-]", x_axis_label="Time", x_range=p1.x_range,
    tools=TOOLS)
    p3.line("datetime", "valve_position", source=source, line_width=2, color="olive", legend="Valve position")

    p4 = figure(height=height, width=width, title="Temperature", x_axis_type="datetime",
    sizing_mode="stretch_width", y_axis_label="Temperature [°C]", x_axis_label="Time", x_range=p1.x_range,
    tools=TOOLS)
    p4.line("datetime", "temperature", source=source, line_width=2, color="orange", legend="Temperature")

    p1.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime' }))
    p2.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))    
    p3.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))    
    p4.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))
        
    p1.legend.location = "top_left"
    p1.legend.click_policy="hide"
    p2.legend.location = "top_left"
    p2.legend.click_policy="hide"
    p3.legend.location = "top_left"
    p4.legend.location = "top_left"

    datetime_range_slider = DatetimeRangeSlider(value=(datetime(2022, 3, 8, 12), datetime(2022, 12, 25, 18)),
                                                start=datetime(2022, 3, 1), end=datetime(2022, 12, 31))
    datetime_range_slider.js_on_change("value", CustomJS(code="""
        console.log('datetime_range_slider: value=' + this.value, this.toString())
    """))

    p1.yaxis.formatter = NumeralTickFormatter(format="0 a")
    p1.xaxis.formatter = DatetimeTickFormatter(months = "%b %Y")
    p2.xaxis.formatter = DatetimeTickFormatter(months = "%b %Y")
    p3.xaxis.formatter = DatetimeTickFormatter(months = "%b %Y")
    p4.xaxis.formatter = DatetimeTickFormatter(months = "%b %Y")
    script, div = components(column(p3,p1,p2,p4,sizing_mode='stretch_both'),column(datetime_range_slider))
    
    return script, div
