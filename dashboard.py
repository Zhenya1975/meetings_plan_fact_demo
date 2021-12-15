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
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_bootstrap_templates import load_figure_template
from dash import dash_table
import plotly.graph_objects as go
import meeting_plan_fact
import tab_plan_fact
import functions_file
import tab_settings
import initial_values



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
                                tab_settings.tab_settings(),
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
    Output("managers_selector_checklist_tab_plan_fact", "value"),
    Output("managers_selector_checklist_tab_plan_fact", "options"),
    Output('meetings_plan_fact_graph', 'figure'),
    Output('users_plan_fact_table', 'children'),
   ],

    [
        Input('quarter_selector', 'value'),
        Input('year_selector', 'value'),
        Input('select_all_regions_button_tab_plan_fact', 'n_clicks'),
        Input('release_all_regions_button_tab_plan_fact', 'n_clicks'),
        Input('region_selector_checklist_tab_plan_fact', 'value'),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input('select_all_managers_button_tab_plan_fact', 'n_clicks'),
        Input('release_all_managers_button_tab_plan_fact', 'n_clicks'),
        Input('managers_selector_checklist_tab_plan_fact', 'value'),
        Input('meetings_data_selector', 'value'),

   ])
def cut_selection_by_quarter(quarter_selector, year_selector, select_all_regions_button, release_all_regions_button, region_selector_selected_list, theme_selector, select_all_users_button, release_all_users_button, managers_from_checklist, meetings_data_selector):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # Обработчик кнопок Снять / Выбрать в блоке Регионы
    id_select_all_regions_button = "select_all_regions_button_tab_plan_fact"
    id_release_all_regions_button = "release_all_regions_button_tab_plan_fact"

    region_list_options = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[1]
    region_list_value_full = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[2]

    if region_selector_selected_list:
        region_list_value = region_selector_selected_list
    else:
        region_list_value = region_list_value_full

    id_checklist_region = 'region_selector_checklist_tab_plan_fact'
    # если кликнули по чек-листу, то берем значение из выбранного списка
    if id_checklist_region in changed_id:
        region_list_value = region_selector_selected_list

    # при клике на кнопку Выбрать все - выбираем все и наоборот
    if id_select_all_regions_button in changed_id:
        region_list_value = region_list_value_full
    elif id_release_all_regions_button in changed_id:
        region_list_value = []


    # данные, обрезанные по датам начала и конца квартала
    data_selected_quarter = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[0]

    ################# блок получения данных для чек-листа пользователей ################
    users_data = functions_file.get_unique_users(data_selected_quarter, region_list_value, managers_from_checklist)
    users_list_options = users_data[0]
    users_list_values = users_data[1]

    id_checklist_users = 'managers_selector_checklist_tab_plan_fact'
    if id_checklist_users in changed_id:
        users_list_values = managers_from_checklist

    # Обработчик кнопок Снять / Выбрать в блоке Пользователи
    id_select_all_users_button = "select_all_managers_button_tab_plan_fact"
    id_release_all_users_button = "release_all_managers_button_tab_plan_fact"

    if id_select_all_users_button in changed_id:
        users_list_options = users_data[0]
        users_list_values = users_data[1]
    elif id_release_all_users_button in changed_id:
        users_list_options = users_data[0]
        users_list_values = []


    # фильтруем датафрейм по выбранным в чек-листе регионам и пользователям:
    events_df_selected_by_quarter_filtered_by_regions = data_selected_quarter.loc[data_selected_quarter['region_code'].isin(region_list_value) & data_selected_quarter['user_id'].isin(users_list_values)]

    ###### готовим данные для построения графика ########
    meetings_fact_graph_data = events_df_selected_by_quarter_filtered_by_regions.groupby('close_date', as_index=False)["qty"].sum()
    quarter_dates_df = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[3]
    df_meetings_fact_graph = pd.merge(quarter_dates_df, meetings_fact_graph_data, on='close_date', how='left')
    df_meetings_fact_graph.fillna(0, inplace=True)
    df_meetings_fact_graph.loc[:, 'cumsum'] = df_meetings_fact_graph['qty'].cumsum()
    df_meetings_fact_graph = df_meetings_fact_graph.astype({"cumsum": int})
    x = df_meetings_fact_graph['close_date']
    y = df_meetings_fact_graph['cumsum']
    fact_at_current_date = df_meetings_fact_graph.iloc[-1]['cumsum']
    ########### ГРАФИК ФАКТ ВСТРЕЧ #######################

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
    start_date = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[4].strftime("%d.%m.%Y")
    finish_date = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[5].strftime("%d.%m.%Y")

    customer_data_df = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[6]
    customer_data_df = customer_data_df.loc[customer_data_df['region_code'].isin(region_list_value) & customer_data_df['user_id'].isin(users_list_values)]

    plan_value = customer_data_df['visit_plan'].sum()
    annotation_text = "    План посещений: " + str(plan_value) + " визитов"


    fig.add_hline(y=plan_value, line_width=3, line_color="red", annotation_text=annotation_text,
                  annotation_position="top left",
                  annotation_font_size=15,
                  annotation_font_color="red",

                  )


    fig.update_layout(
        template=graph_template,
        xaxis={'range': [start_quarter_date, finish_quarter_date]},
        title='Завершено: {}<br><sup>c {} по {}</sup> '.format(fact_at_current_date, start_date, finish_date),
    )

    ############# Таблица с данными о выполнении плана сотрудниками ################
    # Имя пользователя. План. Факт. Статус выполнения плана
    customer_visit_plan_df = meeting_plan_fact.prepare_meetings_fact_data(quarter_selector, year_selector, region_selector_selected_list, meetings_data_selector)[6]

    customer_visit_plan_filtered_df = customer_visit_plan_df.loc[customer_visit_plan_df['region_code'].isin(region_list_value)]
    user_plan_df = customer_visit_plan_filtered_df.groupby(['user_id'],as_index=False)[['visit_plan']].sum()
    fact_df = events_df_selected_by_quarter_filtered_by_regions.groupby(['user_id'],as_index=False)['qty'].sum()

    plan_fact_df = pd.merge(user_plan_df, fact_df, on='user_id', how='left')
    plan_fact_df.fillna(0, inplace=True)
    plan_fact_df = plan_fact_df.astype({"qty": int})
    plan_fact_df = plan_fact_df.loc[plan_fact_df['user_id'].isin(users_list_values)]
    plan_fact_df.rename(columns={'qty': 'visit_fact'}, inplace=True)
    plan_fact_df['delta'] = plan_fact_df['visit_plan'] - plan_fact_df['visit_fact']
    plan_fact_df['status'] = 0
    for index, row in plan_fact_df.iterrows():
        if row['delta'] < 0:
            row['status'] = 1
        else:
            row['status'] = 0
    users_plan_fact_table_data = pd.merge(plan_fact_df, initial_values.users_df, on='user_id', how='left')
    users_plan_fact_table_data['Менеджер'] = users_plan_fact_table_data['name'] + ', ' + users_plan_fact_table_data['position']
    users_plan_fact_table_df = users_plan_fact_table_data.loc[:, ['Менеджер', 'visit_plan', 'visit_fact', 'status']]
    status_dict = {0: "Не выполнен", 1: "Выполнен"}
    users_plan_fact_table_df['status'] = users_plan_fact_table_df['status'].map(status_dict)
    users_plan_fact_table_df.rename(columns={'visit_plan': 'План визитов', 'visit_fact': 'Факт визитов', 'status': 'Статус выполнения плана'}, inplace=True)


    users_plan_fact_table = dash_table.DataTable(
                            # id='table',
                            columns=[{"name": i, "id": i} for i in users_plan_fact_table_df.columns],
                            data=users_plan_fact_table_df.to_dict('records'),
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                            },
                            style_cell={'textAlign': 'left'},
                        )

    return region_list_value, region_list_options, users_list_values, users_list_options, fig, users_plan_fact_table


if __name__ == "__main__":
    app.run_server(debug=True)