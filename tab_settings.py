from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def tab_settings():
    tab_settings_block = dcc.Tab(
        label='Настройки',
        value='tab_settings',
        # className='custom-tab',
        # selected_className='custom-tab--selected',
        children=[dbc.Row([
            dbc.Alert("This is one column", color="primary",
                      # dismissable=True,
                      duration=4000,
                      ),

            dbc.Col(
                #width=3,
                children=[
                    html.Div(id='alert_upload'),
                    html.P('В отчет План-факт встреч включить:'),
                    dcc.RadioItems(
                        id = 'meetings_data_selector',
                        options=[
                            {'label': ' Все завершенные встречи', 'value': 'include_all_meetings'},
                            {'label': ' Только встречи, идущие в зачет погашения нормы визитов', 'value': 'include_plan_fact_meetings'},
                        ],
                        value='include_plan_fact_meetings',
                        labelStyle=dict(display='block'),
                    ),
                    html.Hr(),
                    dcc.Upload(dbc.Button("Загрузить встречи", color="secondary",
                                          size="md",
                                          style={'marginBottom': '3px',
                                                 'marginTop': '3px',
                                                 'backgroundColor': '#232632'},
                                          ),
                               id="upload_meetings"
                               ),
                    html.Div([
                        html.A("Выгрузить Excel шаблон встреч",
                               style={'color': 'blue', 'text-decoration': 'none'},
                               id="btn_xlsx"),
                        dcc.Download(id="download-meetings-xlsx"),
                    ]),
                ]


                    )
        ]

        )]

    )
    return tab_settings_block