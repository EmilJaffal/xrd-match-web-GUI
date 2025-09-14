import dash
from dash import html, dcc

# Initialize the Dash app.
app = dash.Dash(__name__)
server = app.server

# Upload field style.
upload_style = {
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'margin': '10px auto',
    'backgroundColor': 'lightgrey',
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    "fontSize": "24px",
    "fontWeight": "normal"
}

# Predefine lattice parameter blocks for up to 5 CIF files.
# Each block is initially hidden (display: none).
max_files = 5
lattice_params_blocks = []
for i in range(1, max_files + 1):
    block = html.Div(
        id=f"lattice-params-{i}",
        style={
            "position": "relative",  # for absolute positioning of buttons
            "border": "1px solid #ccc",
            "padding": "18px",  # increased padding for a bigger window
            "marginBottom": "8px",
            "display": "none",
            "fontSize": "24px",  # roughly 1.5× the base size
            "fontWeight": "normal"
        },
        children=[
            # Reset and Delete buttons (top-right corner)
            html.Div([
                html.Button(
                    "Reset",
                    id=f"reset-{i}",
                    n_clicks=0,
                    style={
                        "backgroundColor": "lightgrey",
                        "color": "white",
                        "fontSize": "14px",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "4px 8px",
                        "width": "100px",
                        "marginRight": "10px"
                    }
                ),
                html.Button(
                    "Delete",
                    id=f"delete-{i}",
                    n_clicks=0,
                    style={
                        "backgroundColor": "red",
                        "color": "white",
                        "fontSize": "14px",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "4px 8px",
                        "width": "100px"
                    }
                )
            ], style={"position": "absolute", "top": "10px", "right": "10px", "display": "flex"}),
            html.H4(id=f"lattice-params-header-{i}", children=f"CIF File {i}", style={"textAlign": "center", "marginTop": "0px", "marginBottom": "5px", "fontWeight": "normal"}),
            # Lattice parameters for each block:
            
            html.Div([
                html.H5("Cell parameters", style={"textAlign": "center", "marginTop": "0px", "marginBottom": "0px", "paddingTop": "0px", "paddingBottom": "0px", "fontWeight": "normal"}),  # Cell parameters heading
                # Row for a, b, c:
                
            html.Div([
                html.Div([
                    html.Label("a:"),
                    dcc.Input(
                        id=f"lattice-{i}-a",
                        type="number",
                        step=0.1,
                        style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                    )
                ], style={"display": "inline-block", "marginRight": "10px"}),

                html.Div([
                    html.Label("b:"),
                    dcc.Input(
                        id=f"lattice-{i}-b",
                        type="number",
                        step=0.1,
                        style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                    )
                ], style={"display": "inline-block", "marginRight": "10px"}),

                html.Div([
                    html.Label("c:"),
                    dcc.Input(
                        id=f"lattice-{i}-c",
                        type="number",
                        step=0.1,
                        style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                    )
                ], style={"display": "inline-block", "marginRight": "10px"}),

                html.Div([
                    html.Div([
                        html.Label("α:"),
                        dcc.Input(
                            id=f"lattice-{i}-alpha",
                            type="number",
                            style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                        )
                    ], style={"display": "inline-block", "marginRight": "10px"}),

                    html.Div([
                        html.Label("β:"),
                        dcc.Input(
                            id=f"lattice-{i}-beta",
                            type="number",
                            style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                        )
                    ], style={"display": "inline-block", "marginRight": "10px"}),

                    html.Div([
                        html.Label("γ:"),
                        dcc.Input(
                            id=f"lattice-{i}-gamma",
                            type="number",
                            style={"width": "100px", "height": "28px", "fontSize": "18px", "margin": "15px"}
                        )
                    ], style={"display": "inline-block", "marginRight": "10px", "fontSize": "18px"})
                ], style={"display": "flex", "alignItems": "center", "fontSize": "18px"})
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "10px"})]),

        html.Div([
            # Intensity scaling slider
            html.Div([
                html.Label("Intensity scaling:"),
                dcc.Slider(
                    id=f"intensity-{i}",
                    min=0,
                    max=150,
                    step=1,
                    value=100,
                    marks={i: str(i) for i in range(0, 151, 10)},  # Customize marks for slider ticks
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"flex": "1 1 300px", "marginRight": "10px", "fontSize": "18px"}),  # Adjusted for flex

            # Background level slider
            html.Div([
                html.Label("Background level:"),
                dcc.Slider(
                    id=f"background-{i}",
                    min=0,
                    max=100,
                    step=1,
                    value=0,
                    marks={i: str(i) for i in range(0, 101, 10)},  # Customize marks for slider ticks
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"flex": "1 1 300px", "marginRight": "10px", "fontSize": "18px", "fontFamily": "Open Sans"}),  # Adjusted for flex

            # Shift unit cell slider
            html.Div([
                html.Label("Shift unit cell:"),
                dcc.Slider(
                    id=f"lattice-scale-{i}",
                    min=-5,
                    max=5,
                    step=0.1,
                    value=0,
                    marks={j: f"{j}%" for j in range(-5, 6)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"flex": "1 1 300px", "marginRight": "10px", "fontSize": "18px"})  # Adjusted for flex
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "10px"})
        ]
    )
    lattice_params_blocks.append(block)

app.layout = html.Div(
    style={"fontFamily": "Open Sans", "fontSize": "16px"},  # Global font style.
    children=[
        html.Div(
            children=[
                html.H1("XRD Pattern Customizer", style={"fontSize": "32px", "fontWeight": "normal"}),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",  # Centers horizontally
                "alignItems": "center",      # Centers vertically
                "height": "5vh",           # Full height of the viewport
                "textAlign": "center"        # Ensures text is centered
            }
        ),
        
        # Upload Section for .xy file.
        html.Div([
            # XY file upload container.
            html.Div([
                html.Div(
                    dcc.Upload(
                        id="upload-xy",
                        children=html.Div("Drop an .xy file or click to select"),
                        multiple=False,
                        accept=".xy",
                        style=upload_style
                    ),
                    style={"width": "90%", "display": "inline-block", "verticalAlign": "top"}
                ),
                html.Div(
                    html.Span(
                        id="xy-upload-status",
                        style={
                            "margin-left": "10px",
                            "color": "green",
                            "fontSize": "24px",
                            "position": "relative",
                            "textAlign": "center",
                            "left": "20px",
                            "top": "20px"
                        }
                    ),
                    style={"width": "10%", "display": "inline-block", "verticalAlign": "middle"}
                )
            ], style={"width": "50%", "display": "inline-block"})
        ], style={"display": "flex", "width": "100%"}),

        # CIF file upload container.
        html.Div([
            html.Div(
                dcc.Upload(
                    id="upload-cif",
                    children=html.Div("Drop one or more .cif files or click to select (do this first)"),
                    multiple=True,
                    accept=".cif",
                    style=upload_style
                ),
                style={"width": "90%", "display": "inline-block", "verticalAlign": "top", "fontWeight": "normal"}
            ),
            html.Div(
                html.Span(
                    id="cif-upload-status",
                    style={
                        "margin-left": "10px",
                        "color": "green",
                        "fontSize": "24px",
                        "position": "relative",
                        "textAlign": "center",
                        "left": "20px",
                        "top": "20px"
                    }
                ),
                style={"width": "10%", "display": "inline-block", "verticalAlign": "middle"}
            )
        ], style={"width": "50%", "display": "inline-block"}),
        
        # Lattice Parameters Container (predefined blocks).
        html.Div(id="lattice-params-container", children=lattice_params_blocks),
        
        # Pattern opacities, experimental intensity scaling, and 2θ range side by side
        html.Div([
            html.Div([
                html.Label("Pattern opacities:"),
                dcc.Slider(
                    id="opacity-slider",
                    min=0,
                    max=1,
                    step=0.1,
                    value=0.9,
                    marks={i/10: str(i*10) for i in range(11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"fontSize": "18px", "width": "14.3%", "marginLeft": "21px", "marginRight": "10px", "display": "inline-block", "verticalAlign": "middle"}),

            html.Div([
                html.Label("Experimental intensity scaling:"),
                dcc.Slider(
                    id="exp-intensity-slider",
                    min=0,
                    max=200,
                    step=1,
                    value=100,
                    marks={i: str(i) for i in range(0, 201, 20)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"fontSize": "18px", "width": "14.3%", "marginRight": "10px", "display": "inline-block", "verticalAlign": "middle"}),

            html.Div([
                html.Label("2θ range:"),
                dcc.RangeSlider(
                    id="xrange-slider",
                    min=0,
                    max=120,
                    step=1,
                    value=[10, 120],
                    marks={i: str(i) for i in range(0, 121, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"fontSize": "18px", "width": "14.3%", "display": "inline-block", "verticalAlign": "middle"})
        ], style={"marginTop": "10px", "marginBottom": "10px", "width": "100%", "display": "flex", "alignItems": "center"}),

        # Download Plot button.
        html.Div([
            html.A(
                html.Button("Download plot", style={
                    "margin-left": "10px",
                    "padding": "9px 18px",  # Increased from 6px 12px
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "4px",
                    "cursor": "pointer",
                    "fontSize": "20px"  # Increased font size for 1.5× effect
                }),
                id="download-link",
                download="xrd_pattern.png",
                href="",
                target="_blank"
            )
        ], style={"marginTop": "10px", "marginBottom": "10px"}),
        
        # XRD Plot.
        html.Div([
            dcc.Graph(id="xrd-plot")
        ], id="plot-container", style={"width": "100%", "height": "1000px"}),
        
        # Hidden stores.
        dcc.Store(id="cif-store"),
        dcc.Store(id="xy-store"),
        dcc.Store(id="cif-order-store")
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)