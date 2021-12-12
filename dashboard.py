"""
This is a minimal example of changing themes with the ThemeSwitchAIO component
Note - this requires dash-bootstrap-components>=1.0.0 and dash>=2.0
    pip install dash-bootstrap-templates=1.0.0.

The ThemeSwitchAIO component updates the Plotly default figure template when the
theme changes, but the figures must be updated in a callback in order to render with the new template.

This example demos:
 - how to update the figure for the new theme in a callback
 - using the dbc class which helps improve the style when the themes are switched. See the dbc.css file in the dash-bootstrap-templates library.

"""

from dash import Dash, dcc, html, Input, Output, callback_context
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_bootstrap_templates import load_figure_template

import meeting_plan_fact
import meetings_plan_fact_graph_data_prepare
import tab_plan_fact
import functions_file
import plotly.graph_objects as go

# select the Bootstrap stylesheet2 and figure template2 for the theme toggle here:
# template_theme1 = "sketchy"
template_theme1 = "flatly"
template_theme2 = "darkly"
# url_theme1 = dbc.themes.SKETCHY
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

templates = [
    "bootstrap",
    "minty",
    "pulse",
    "flatly",
    "quartz",
    "cyborg",
    "darkly",
    "vapor",
]

load_figure_template(templates)



dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)
app = Dash(__name__, external_stylesheets=[url_theme1, dbc_css])

"""
===============================================================================
Layout
"""
app.layout = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.H4("ОТЧЕТЫ", className="bg-primary text-white p-4 mb-2"),
                    ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],),

                    html.Div([
                        dcc.Tabs(
                            id="tabs-all",
                            value='tab_plan_fact',
                            # parent_className='custom-tabs',
                            # className='custom-tabs-container',
                            children=[
                                tab_plan_fact.tab_plan_fact(),
                                # tab_calendar_actions.calendar_actions(),
                                # tab_settings.tab_settings(),
                                # tab2(),
                                # tab3(),
                            ]
                        ),
                    ]),

                ]
            )
        ]
    ),
    className="m-4 dbc",
    fluid=True,
)

@app.callback([
    Output("region_selector_checklist_tab_plan_fact", "value"),
    Output("region_selector_checklist_tab_plan_fact", "options"),
    Output('meetings_plan_fact_graph', 'figure'),
   ],

    [
        Input('quarter_selector', 'value'),
        Input('year_selector', 'value'),
        Input('select_all_regions_button_tab_plan_fact', 'n_clicks'),
        Input('release_all_regions_button_tab_plan_fact', 'n_clicks'),
        Input('region_selector_checklist_tab_plan_fact', 'value'),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),

   ])
def cut_selection_by_quarter(quarter_selector, year_selector, select_all_regions_button, release_all_regions_button, region_selector_selected_list, theme_selector):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # Обработчик кнопок Снять / Выбрать в блоке Регионы
    id_select_all_button = "select_all_regions_button_tab_plan_fact"
    id_release_all_button = "release_all_regions_button_tab_plan_fact"

    region_list_options = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[1]
    region_list_value_full = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[2]

    region_list_value = region_list_value_full
    if id_select_all_button in changed_id:
        region_list_value = region_list_value_full
    elif id_release_all_button in changed_id:
        region_list_value = []

    id_checklist_region = 'region_selector_checklist_tab_plan_fact'
    if id_checklist_region in changed_id:
        region_list_value = region_selector_selected_list
    # данные, обрезанные по датам начала и конца квартала
    data_selected_quarter = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[0]

    #########################
    # фильтруем датафрейм по выбранным в чек-листе регионам:
    events_df_selected_by_quarter_filtered_by_regions = data_selected_quarter.loc[data_selected_quarter['region_code'].isin(region_list_value)]

    ###### готовим данные для построения графика ########
    meetings_fact_graph_data = meetings_plan_fact_graph_data_prepare.meetings_plan_fact_graph_data(events_df_selected_by_quarter_filtered_by_regions)
    quarter_dates_df = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[3]
    df_meetings_fact_graph = pd.merge(quarter_dates_df, meetings_fact_graph_data, on='close_date', how='left')
    df_meetings_fact_graph.fillna(0, inplace=True)
    df_meetings_fact_graph.loc[:, 'cumsum'] = df_meetings_fact_graph['qty'].cumsum()
    df_meetings_fact_graph = df_meetings_fact_graph.astype({"cumsum": int})
    x = df_meetings_fact_graph['close_date']
    y = df_meetings_fact_graph['cumsum']
    fact_at_current_date = df_meetings_fact_graph.iloc[-1]['cumsum']
    
    if theme_selector:
        graph_template = 'bootstrap'
    else:
        graph_template = 'plotly_dark'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill='tozeroy',
        name='Завершенные встречи, кол-во',
    ))

    start_quarter_date = functions_file.quarter_important_days(quarter_selector, year_selector)[0]
    finish_quarter_date = functions_file.quarter_important_days(quarter_selector, year_selector)[1]
    start_date = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[4].strftime("%d.%m.%Y")
    finish_date = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list)[5].strftime("%d.%m.%Y")

    fig.update_layout(
        template=graph_template,
        xaxis={'range': [start_quarter_date, finish_quarter_date]},
        title='Завершено: {}<br><sup>c {} по {}</sup> '.format(fact_at_current_date, start_date, finish_date),
    )
    
    return region_list_value, region_list_options, fig



if __name__ == "__main__":
    app.run_server(debug=True)