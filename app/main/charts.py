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
    #'https://twin.svsfem.cz/api/data/lastchart'
    #'http://127.0.0.1:5000/api/data/lastchart'
    
    adapter = CustomJS(code="""
    const hydrodata = cb_data.response
    const result = {datetime: [Date.parse(hydrodata["datetime"])], pressure1: [hydrodata["pressure1"]], pressure2: [hydrodata["pressure2"]],
                    flow1: [hydrodata["flow1"]],flow2: [hydrodata["flow2"]], valve_position: [hydrodata["valve_position"]], 
                    temperature: [hydrodata["temperature"]],PressureMonitor1: [hydrodata["PressureMonitor1"]],
                    PressureMonitor2: [hydrodata["PressureMonitor2"]],FlowMonitor1: [hydrodata["FlowMonitor1"]], FlowMonitor2: [hydrodata["FlowMonitor2"]]} 
    console.log(result)
    return result
""")
    
    source = AjaxDataSource(data_url='https://twin.svsfem.cz/api/data/lastchart',
                            polling_interval=5000, method= "GET", mode='append',adapter=adapter)
    print(source.data)
    # adapter, content_type, data, data_url, http_headers,
    # if_modified, js_event_callbacks, js_property_callbacks, max_size, method, mode, name, polling_interval, selected, selection_policy, subscribed_events, syncable or tags
    tooltips = [
        ("time", "@datetime{%F %T}"),
        ("value", "$y{0.0}")
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
    p1.square("datetime", "pressure2", source=source, size=10, color="firebrick", fill_color="white")

    p1.line("datetime", "PressureMonitor1", source=source, line_width=2, color="navy",line_dash="dashed",legend="DT Pressure1")
    p1.circle_x("datetime", "PressureMonitor1", source=source, size=10, color="navy", fill_color="white")
    p1.line("datetime", "PressureMonitor2", source=source, line_width=2, color="firebrick",line_dash="dashed",legend="DT Pressure2")
    p1.square_x("datetime", "PressureMonitor2", source=source, size=10, color="firebrick", fill_color="white")

    p2 = figure(height=height, width=width, title="Flow", x_axis_type="datetime", sizing_mode="stretch_width",
    y_axis_label="Flow rate [l/h]",x_axis_label="Time",x_range=p1.x_range, tools=TOOLS)

    p2.line("datetime", "FlowMonitor1", source=source, line_width=2, color="navy", legend="Flow1")
    p2.circle("datetime", "FlowMonitor1", source=source, size=10, color="navy", fill_color="white")
    p2.line("datetime", "FlowMonitor2", source=source, line_width=2, color="firebrick", legend="Flow2")
    p2.triangle("datetime", "FlowMonitor2", source=source, size=10, color="firebrick", fill_color="white")   

    p2.line("datetime", "flow1", source=source, line_width=2, color="navy", line_dash="dashed", legend="DT Flow1")
    p2.circle_x("datetime", "flow1", source=source, size=10, color="navy", fill_color="white")
    p2.line("datetime", "flow2", source=source, line_width=2, color="firebrick", line_dash="dashed", legend="DT Flow2")
    p2.square_x("datetime", "flow2", source=source, size=10, color="firebrick", fill_color="white")  

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
    p1.x_range.follow_interval = 5000
    p2.x_range.follow = "end"
    p2.x_range.follow_interval = 5000
    p3.x_range.follow = "end"
    p3.x_range.follow_interval = 5000
    p4.x_range.follow = "end"
    p4.x_range.follow_interval = 5000
    p1.legend.location = "top_left"
    p1.legend.click_policy="hide"
    p2.legend.location = "top_left"
    p2.legend.click_policy="hide"
    p3.legend.location = "top_left"
    p4.legend.location = "top_left"

    p1.add_tools(HoverTool(tooltips=tooltips, formatters={'@datetime': 'datetime'}))
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
    sql_query1 = pd.read_sql("data",'sqlite:///app.db',index_col=["id"],coerce_float=False,
                            columns=["datetime","pressure1","pressure2","flow1","flow2","temperature","valve_position"],
                            parse_dates=["datetime"])
    sql_query2 = pd.read_sql("fmu_data",'sqlite:///app.db',index_col=["id"],coerce_float=False,
                            columns=['datetime', 'Ball_Valve_Pressure_drop', 'Bend_Pressure_drop',
                                    'Control_Valve_Static_pressure_diff', 'FlowMonitor1', 'FlowMonitor2',
                                    'ManometrMonitor','PressureMonitor1','PressureMonitor2','Pump_pressure_rise'],
                            parse_dates=["datetime"])
    df1 = pd.DataFrame(sql_query1)
    df2 = pd.DataFrame(sql_query2)
    df = pd.concat([df1, df2], axis=1)
    print(df)
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
    p1.line("datetime", "PressureMonitor1", source=source, line_width=2, color="navy", line_dash="dashed",legend="DT Pressure1")
    p1.line("datetime", "PressureMonitor2", source=source, line_width=2, color="firebrick", line_dash="dashed", legend="DT Pressure2")    

    p2 = figure(height=height, width=width, title="Flow", x_axis_type="datetime", sizing_mode="stretch_width",
    y_axis_label="Flow rate [m3/h]",  x_axis_label="Time", x_range=p1.x_range,  tools=TOOLS)

    p2.line("datetime", "flow1", source=source, line_width=2, color="navy", legend="Flow1")
    p2.line("datetime", "flow2", source=source, line_width=2, color="firebrick", legend="Flow2")
    p2.line("datetime", "FlowMonitor1", source=source, line_width=2, color="navy", line_dash="dashed", legend="DT Flow1")
    p2.line("datetime", "FlowMonitor2", source=source, line_width=2, color="firebrick", line_dash="dashed", legend="DT Flow2")   

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
