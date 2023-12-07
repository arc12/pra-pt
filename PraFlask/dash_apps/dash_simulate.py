# import logging
from random import shuffle

from pg_shared.dash_utils import create_dash_app_util

from pra import core, menu, Langstrings
from flask import session

from dash import html, dcc, callback_context, no_update
from dash.exceptions import PreventUpdate

from dash.dependencies import Output, Input, State

view_name = "simulate"

def create_dash(server, url_rule, url_base_pathname):
    """Create a Dash view"""
    app = create_dash_app_util(server, url_rule, url_base_pathname)

    # dash app definitions goes here
    app.config.suppress_callback_exceptions = True
    app.title = "Simulate Precision, Recall, and Accuracy"

    app.layout = html.Div([
        dcc.Location(id="location"),
        dcc.Store(id="shuffled", storage_type="memory"),
        dcc.Store(id="tpr_lookup", storage_type="memory"),

        html.Div(id="menu"),

        html.Div(
            [
                html.H1(id="heading", className="header-title")
            ]
            # className="header"
            ),
        
        html.Div([html.Label(id="roc_label"), dcc.Dropdown(id="roc_key", className="mx-2")], className="d-flex justify-content-start"),

        html.Div(
            [
                html.Div(dcc.Slider(id="cf_slider", min=5, max=95, step=5, value=50, marks=None, tooltip={"placement": "bottom", "always_visible": True}, className="mx-2"), style={"width": "35%"}),
                html.Div(dcc.Slider(id="specificity_slider", min=0, value=0, marks=None, tooltip={"placement": "bottom", "always_visible": True}, className="mx-2"), style={"width": "35%"})
            ],
            className="d-flex justify-content-start"
        ),

        html.Div(
            dcc.Loading(
                dcc.Graph(id="scatter_grid", config={'displayModeBar': False}),
                type="circle"
            )
        ),

        html.Div(
            dcc.Loading(
                dcc.Graph(id="metric_bars", config={'displayModeBar': False}),
                type="circle"
            )
        )

    ],
    className="wrapper"
    )

    @app.callback(
            [
                Output("scatter_grid", "figure"),
                Output("metric_bars", "figure")
            ],
            [
                Input("cf_slider", "value"),
                Input("specificity_slider", "value"),
                Input("tpr_lookup", "data")
            ],
            [
                State("specificity_slider", "step"),
                State("shuffled", "data")
            ]
    )
    def compute(cf_slider, specificity_slider, tpr_lookup, specificity_slider_step, shuffled):
        # triggered_by = callback_context.triggered_id
        if tpr_lookup is None:
            raise PreventUpdate
        
        class_fraction = cf_slider / 100  # display is %
        n = len(shuffled)
        n_c1 = int(round(n * class_fraction, 0))
        n_c0 = n - n_c1

        fp_rate = 1 - specificity_slider
        lookup_index = int(round(fp_rate / specificity_slider_step, 0)) - 1
        tp_rate = tpr_lookup[lookup_index]

        tp = int(round(tp_rate * n_c1, 0))
        fp = int(round(fp_rate * n_c0, 0))
        tn = n_c0 - fp
        fn = n_c1 - tp
        print(tp, fp, tn, fn)

        # scatter grid - visualise the TP/FP
        # the values, v, in shuffled give a position in the scatter plot: x = v % D, y = v // M, where D is the dimension given in config = sqrt(len(shuffled))
        # split shuffled into two, first part for cls=0 and second for cls=1
        # true predictions are taken from the start of each split, and false from the end. i.e. count in from each end.
        from math import sqrt
        d = sqrt(n)
        c0_v = shuffled[:n_c0]
        c1_v = shuffled[n_c0:]
        tp_v = c1_v[:tp]
        fp_v = c0_v[-fp:]
        fn_v = c1_v[-fn:]
        scatter_grid = {
            "data": [
                # add 0.5 to inset from border/axes
                {
                    "x": [v % d + 0.5 for v in tp_v],
                    "y": [v // d + 0.5 for v in tp_v],
                    "name": "TP",  # TODO langstring
                    "mode": "markers",
                    "marker": {"color": "red", "symbol": "circle", "size": 10},
                    "hoverinfo": "skip"
                },
                {
                    "x": [v % d + 0.5 for v in fp_v],
                    "y": [v // d + 0.5 for v in fp_v],
                    "name": "FP",  # TODO langstring
                    "mode": "markers",
                    "marker": {"color": "blue", "symbol": "x", "size": 10},
                    "hoverinfo": "skip"
                },
                {
                    "x": [v % d + 0.5 for v in fn_v],
                    "y": [v // d + 0.5 for v in fn_v],
                    "name": "FN",  # TODO langstring
                    "mode": "markers",
                    "marker": {"color": "red", "symbol": "circle-open", "size": 10},
                    "hoverinfo": "skip"
                }
            ],
            "layout": {
                # "title": "Hit and Miss",  # TODO langstring
                # TODO move legend to bottom
                "xaxis": {"showgrid": False, "showticklabels": False, "showline": True, "mirror": True, "fixedrange": True, "range": [0, d]},
                "yaxis": {"showgrid": False, "showticklabels": False, "showline": True, "mirror": True, "fixedrange": True, "range": [0, d]},
                "margin": {"l": 5, "r": 5, "b": 50, "t": 30},
                "width": 300, "height": 300,
                "legend": {"orientation": "h", "xanchor": "left", "x": 0, "yanchor": "top", "y": -0.01}
            }
        }

        # metrics
        precision = round(tp / (tp + fp), 2) * 100
        recall = round(tp / (tp + fn), 2) * 100
        accuracy = round((tp + tn) / n, 2) * 100
        pos_frac = round((tp + fp) / n, 2) * 100

        metric_bars = {
            "data": [
                {
                    "y": ["Precision", "Recall", "Accuracy"],  # TODO make these langstrings (? how best to pass to client, or maybe set in initial/loading callback and only change values in clientside callback)
                    "x": [precision, recall, accuracy],
                    "text": [f"Precision={precision:.0f}%", f"Recall={recall:.0f}%", f"Accuracy={accuracy:.0f}%"],
                    "type": "bar",
                    "orientation": "h"
                }
            ],
            "layout": {
                "title": "Metrics",  # TODO langstring
                "yaxis": {"fixedrange": True},
                "xaxis": {"title": "%", "fixedrange": True, "range": [0, 100]},
                "showlegend": False,
                "margin": {"l": 00, "r": 0, "b": 30, "t": 30},
                "height": 150
            }
        }

        return [scatter_grid, metric_bars]
    
    @app.callback(
        [
            Output("tpr_lookup", "data")  # use Store as the slider callback will ultimately be client side
        ],
        [
            Input("roc_key", "value"),
            Input("location", "pathname"),
            Input("location", "search")
        ]
    )
    def change_roc(roc_key, pathname, querystring):
            
        specification_id = pathname.split('/')[-1]
        spec = core.get_specification(specification_id)
        # langstrings = Langstrings(spec.lang)

        rocs = spec.load_asset_json("rocs")
        use_spline = rocs[roc_key]
        
        return[use_spline["y"]]

    @app.callback(
        [
            Output("menu", "children"),
            Output("heading", "children"),
            Output("roc_label", "children"),
            Output("roc_key", "options"),
            Output("roc_key", "value"),
            Output("cf_slider", "value"),
            Output("specificity_slider", "max"),
            Output("specificity_slider", "step"),
            Output("specificity_slider", "value"),
            Output("shuffled", "data")
        ],
        [
            Input("location", "pathname"),
            Input("location", "search")
        ]
    )
    def update_intialise(pathname, querystring):
        specification_id = pathname.split('/')[-1]
        spec = core.get_specification(specification_id)
        langstrings = Langstrings(spec.lang)
    
        if callback_context.triggered_id == "location":
            # initial load
            menu_children = spec.make_menu(menu, langstrings, core.plaything_root, view_name, query_string=querystring, for_dash=True)

            rocs = spec.load_asset_json("rocs")
            spline_names = list(rocs)
            use_spline_name = spec.detail.get("start_curve", spline_names[0])
            use_spline = rocs[use_spline_name]

            shuffled = list(range(spec.detail.get("scatter_grid_size", 10) ** 2))
            shuffle(shuffled)

            output = [
                menu_children,
                spec.title,
                langstrings.get("ROC_LABEL"),
                spline_names,
                use_spline_name,
                # TODO sliders need labels - from detail in spec
                spec.detail.get("start_class_fraction_pc", no_update),
                1.0 - use_spline["x_step"],  # max specificity
                use_spline["x_step"],
                spec.detail.get("start_specificity", no_update),
                shuffled
                ]
        else:
            output = [no_update] * 10

        return output

    return app.server
