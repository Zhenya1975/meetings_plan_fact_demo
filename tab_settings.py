from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def tab_settings():
    tab_settings_block = dcc.Tab(
        label='Настройки',
        value='tab_settings',
        # className='custom-tab',
        # selected_className='custom-tab--selected',
        children=[dbc.Row([
            dbc.Col(
                #width=3,
                children=[
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
                ]


                    )
        ]

        )]

    )
    return tab_settings_block