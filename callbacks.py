import base64
import pandas as pd
from dash import Input, Output, State, callback_context, no_update
import plotly.graph_objects as go
from layout import app
from preprocess import parse_xy, parse_cif, XRDCalculator #, normalize_structure
from plot import plot_xrd
from pymatgen.core import Structure
import plotly.io as pio
import io
import json

# ------------------------------------------------------------------
# File Upload Check Mark Callbacks
# ------------------------------------------------------------------
@app.callback(
    Output("xy-upload-status", "children"),
    Input("upload-xy", "contents")
)
def update_xy_status(contents):
    if contents:
        return "✓"
    return ""

@app.callback(
    Output("cif-upload-status", "children"),
    Input("upload-cif", "contents")
)
def update_cif_status(contents_list):
    if contents_list:
        return "✓"
    return ""

# ------------------------------------------------------------------
# Store Uploaded Files Callbacks
# ------------------------------------------------------------------
@app.callback(
    Output("xy-store", "data"),
    Input("upload-xy", "contents"),
    State("upload-xy", "filename")
)
def store_xy_file(contents, filename):
    if contents is not None:
        try:
            df = parse_xy(contents)
            max_intensity = df['intensity'].max()
            df['intensity'] = (df['intensity'] / max_intensity) * 100
            return df.to_json(date_format='iso', orient='split')
        except Exception as e:
            print("Error processing XY file:", e)
            return no_update
    return no_update

@app.callback(
    [Output("cif-store", "data"),
     Output("cif-order-store", "data"),
     Output("cif-visibility-store", "data", allow_duplicate=True)],
    Input("upload-cif", "contents"),
    State("upload-cif", "filename"),
    State("cif-store", "data"),
    State("cif-order-store", "data"),
    State("cif-visibility-store", "data"),
    prevent_initial_call=True
)
def store_cif_files(contents_list, filenames, existing_data, existing_order, visibility_state):
    if contents_list is None:
        return existing_data if existing_data is not None else no_update, existing_order if existing_order is not None else no_update, no_update

    cif_data = existing_data.copy() if existing_data else {}
    cif_order = existing_order.copy() if existing_order else []
    visibility = visibility_state.copy() if visibility_state else {}

    for contents, name in zip(contents_list, filenames):
        if name not in cif_order:
            cif_order.append(name)
            visibility[name] = True  # New CIFs are visible by default
        cif_data[name] = contents

    return cif_data, cif_order, visibility

# ------------------------------------------------------------------
# Lattice Parameter Blocks Update Callback
# ------------------------------------------------------------------
@app.callback(
    [Output(f"lattice-params-{i}", "style") for i in range(1, 7)] +
    [Output(f"lattice-params-header-{i}", "children") for i in range(1, 7)] +
    [Output(f"lattice-{i}-a", "value") for i in range(1, 7)] +
    [Output(f"lattice-{i}-b", "value") for i in range(1, 7)] +
    [Output(f"lattice-{i}-c", "value") for i in range(1, 7)] +
    [Output(f"lattice-{i}-alpha", "value") for i in range(1, 7)] +
    [Output(f"lattice-{i}-beta", "value") for i in range(1, 7)] +
    [Output(f"lattice-{i}-gamma", "value") for i in range(1, 7)],
    Input("cif-store", "data"),
    Input("cif-order-store", "data")
)
def update_lattice_params_blocks(cif_data, cif_order):
    style_outputs = []
    header_outputs = []
    a_outputs = []
    b_outputs = []
    c_outputs = []
    alpha_outputs = []
    beta_outputs = []
    gamma_outputs = []
    
    file_names = cif_order if cif_order else []
    num_files = len(file_names)
    
    for i in range(6):
        if i < num_files:
            try:
                structure = parse_cif(cif_data[file_names[i]])
                # structure = normalize_structure(structure)
                lattice = structure.lattice
                # Set style so that visible blocks are inline-block and 50% wide.
                style_outputs.append({
                    "display": "inline-block",
                    "width": "45%",
                    "marginRight": "10px",
                    "position": "relative",
                    "border": "1px solid #ccc",
                    "padding": "20px",
                    "marginBottom": "10px",
                    "fontSize": "24px"
                })
                header_outputs.append(file_names[i])
                a_outputs.append(round(lattice.a, 4))
                b_outputs.append(round(lattice.b, 4))
                c_outputs.append(round(lattice.c, 4))
                alpha_outputs.append(round(lattice.alpha, 4))
                beta_outputs.append(round(lattice.beta, 4))
                gamma_outputs.append(round(lattice.gamma, 4))
            except Exception as e:
                print("Error parsing CIF for lattice block:", e)
                style_outputs.append({"display": "none"})
                header_outputs.append("")
                a_outputs.append(None)
                b_outputs.append(None)
                c_outputs.append(None)
                alpha_outputs.append(None)
                beta_outputs.append(None)
                gamma_outputs.append(None)
        else:
            style_outputs.append({"display": "none"})
            header_outputs.append("")
            a_outputs.append(None)
            b_outputs.append(None)
            c_outputs.append(None)
            alpha_outputs.append(None)
            beta_outputs.append(None)
            gamma_outputs.append(None)
    
    return style_outputs + header_outputs + a_outputs + b_outputs + c_outputs + alpha_outputs + beta_outputs + gamma_outputs

# ------------------------------------------------------------------
# Reset Button Callbacks (One per block)
# ------------------------------------------------------------------
def make_reset_callback(i):
    @app.callback(
        [Output(f"lattice-{i}-a", "value", allow_duplicate=True),
         Output(f"lattice-{i}-b", "value", allow_duplicate=True),
         Output(f"lattice-{i}-c", "value", allow_duplicate=True),
         Output(f"lattice-{i}-alpha", "value", allow_duplicate=True),
         Output(f"lattice-{i}-beta", "value", allow_duplicate=True),
         Output(f"lattice-{i}-gamma", "value", allow_duplicate=True),
         Output(f"lattice-scale-{i}", "value"),
         Output(f"lattice-{i}-a", "style", allow_duplicate=True),
         Output(f"lattice-{i}-b", "style", allow_duplicate=True),
         Output(f"lattice-{i}-c", "style", allow_duplicate=True)],
        Input(f"reset-{i}", "n_clicks"),
        [State("cif-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def reset_block(n_clicks, cif_data, file_name):
        if not cif_data or not file_name:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        try:
            structure = parse_cif(cif_data[file_name])
            # structure = normalize_structure(structure)
            lattice = structure.lattice
            
            # Default style (no blue color)
            default_style = {
                "width": "100px", 
                "height": "28px", 
                "fontSize": "18px", 
                "margin": "15px"
            }
            
            return (round(lattice.a, 4),
                    round(lattice.b, 4),
                    round(lattice.c, 4),
                    round(lattice.alpha, 4),
                    round(lattice.beta, 4),
                    round(lattice.gamma, 4),
                    0,  # Reset shift slider to 0
                    default_style,
                    default_style,
                    default_style)
        except Exception as e:
            print("Error in reset callback for", file_name, ":", e)
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    return reset_block

for i in range(1, 7):
    make_reset_callback(i)

# ------------------------------------------------------------------
# Shift Unit Cell Callbacks (Update a, b, c values and styles)
# ------------------------------------------------------------------
def make_shift_callback(i):
    @app.callback(
        [Output(f"lattice-{i}-a", "value", allow_duplicate=True),
         Output(f"lattice-{i}-b", "value", allow_duplicate=True),
         Output(f"lattice-{i}-c", "value", allow_duplicate=True),
         Output(f"lattice-{i}-a", "style"),
         Output(f"lattice-{i}-b", "style"),
         Output(f"lattice-{i}-c", "style")],
        Input(f"lattice-scale-{i}", "value"),
        [State("cif-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def shift_unit_cell(scale_value, cif_data, file_name):
        if not cif_data or not file_name or scale_value is None:
            return no_update, no_update, no_update, no_update, no_update, no_update
        try:
            structure = parse_cif(cif_data[file_name])
            lattice = structure.lattice
            
            # Calculate scale factor
            scale_factor = 1 + (scale_value / 100)
            
            # Calculate new values
            new_a = round(lattice.a * scale_factor, 4)
            new_b = round(lattice.b * scale_factor, 4)
            new_c = round(lattice.c * scale_factor, 4)
            
            # Determine style based on whether shifted
            if scale_value != 0:
                # Blue style when shifted
                input_style = {
                    "width": "100px", 
                    "height": "28px", 
                    "fontSize": "18px", 
                    "margin": "15px",
                    "color": "blue",
                    "fontWeight": "bold"
                }
            else:
                # Default style
                input_style = {
                    "width": "100px", 
                    "height": "28px", 
                    "fontSize": "18px", 
                    "margin": "15px"
                }
            
            return new_a, new_b, new_c, input_style, input_style, input_style
        except Exception as e:
            print("Error in shift callback for", file_name, ":", e)
            return no_update, no_update, no_update, no_update, no_update, no_update
    return shift_unit_cell

for i in range(1, 7):
    make_shift_callback(i)

# ------------------------------------------------------------------
# Delete Button Callbacks (One per block)
# ------------------------------------------------------------------
def make_delete_callback(i):
    @app.callback(
        [Output("cif-store", "data", allow_duplicate=True),
         Output("cif-order-store", "data", allow_duplicate=True),
         Output("cif-visibility-store", "data", allow_duplicate=True)],
        Input(f"delete-{i}", "n_clicks"),
        [State("cif-store", "data"),
         State("cif-order-store", "data"),
         State("cif-visibility-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def delete_block(n_clicks, cif_data, cif_order, visibility_state, file_name):
        if not cif_data or not file_name:
            return no_update, no_update, no_update
        if n_clicks and file_name in cif_data:
            new_data = cif_data.copy()
            new_order = cif_order.copy() if cif_order else []
            new_visibility = visibility_state.copy() if visibility_state else {}
            new_data.pop(file_name)
            if file_name in new_order:
                new_order.remove(file_name)
            if file_name in new_visibility:
                new_visibility.pop(file_name)
            return new_data, new_order, new_visibility
        return cif_data, cif_order, visibility_state
    return delete_block

for i in range(1, 7):
    make_delete_callback(i)

# ------------------------------------------------------------------
# Toggle Visibility Button Callbacks (One per block)
# ------------------------------------------------------------------
def make_toggle_callback(i):
    @app.callback(
        [Output(f"toggle-{i}", "children"),
         Output(f"toggle-{i}", "style"),
         Output("cif-visibility-store", "data", allow_duplicate=True)],
        Input(f"toggle-{i}", "n_clicks"),
        [State("cif-visibility-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def toggle_cif_visibility(n_clicks, visibility_state, file_name):
        if not file_name or not visibility_state:
            return no_update, no_update, no_update
        
        new_visibility = visibility_state.copy()
        current_state = new_visibility.get(file_name, True)
        new_state = not current_state
        new_visibility[file_name] = new_state
        
        button_text = "Hide" if new_state else "Show"
        button_style = {
            "backgroundColor": "#2196F3" if new_state else "#888",
            "color": "white",
            "fontSize": "14px",
            "border": "none",
            "borderRadius": "8px",
            "padding": "4px 8px",
            "width": "100px",
            "marginRight": "10px"
        }
        
        return button_text, button_style, new_visibility
    return toggle_cif_visibility

for i in range(1, 7):
    make_toggle_callback(i)

# ------------------------------------------------------------------
# XRD Plot Callback (Using Dynamic Lattice Parameters and per-CIF intensity/background)
# ------------------------------------------------------------------
@app.callback(
    Output("xrd-plot", "figure"),
    [
        Input("xy-store", "data"),
        Input("opacity-slider", "value"),
        Input("exp-intensity-slider", "value"),  
        Input("xrange-slider", "value"),
        # Lattice parameter inputs for blocks 1 to 6.
        Input("lattice-1-a", "value"),
        Input("lattice-2-a", "value"),
        Input("lattice-3-a", "value"),
        Input("lattice-4-a", "value"),
        Input("lattice-5-a", "value"),
        Input("lattice-6-a", "value"),
        Input("lattice-1-b", "value"),
        Input("lattice-2-b", "value"),
        Input("lattice-3-b", "value"),
        Input("lattice-4-b", "value"),
        Input("lattice-5-b", "value"),
        Input("lattice-6-b", "value"),
        Input("lattice-1-c", "value"),
        Input("lattice-2-c", "value"),
        Input("lattice-3-c", "value"),
        Input("lattice-4-c", "value"),
        Input("lattice-5-c", "value"),
        Input("lattice-6-c", "value"),
        Input("lattice-1-alpha", "value"),
        Input("lattice-2-alpha", "value"),
        Input("lattice-3-alpha", "value"),
        Input("lattice-4-alpha", "value"),
        Input("lattice-5-alpha", "value"),
        Input("lattice-6-alpha", "value"),
        Input("lattice-1-beta", "value"),
        Input("lattice-2-beta", "value"),
        Input("lattice-3-beta", "value"),
        Input("lattice-4-beta", "value"),
        Input("lattice-5-beta", "value"),
        Input("lattice-6-beta", "value"),
        Input("lattice-1-gamma", "value"),
        Input("lattice-2-gamma", "value"),
        Input("lattice-3-gamma", "value"),
        Input("lattice-4-gamma", "value"),
        Input("lattice-5-gamma", "value"),
        Input("lattice-6-gamma", "value"),
        Input("lattice-scale-1", "value"),
        Input("lattice-scale-2", "value"),
        Input("lattice-scale-3", "value"),
        Input("lattice-scale-4", "value"),
        Input("lattice-scale-5", "value"),
        Input("lattice-scale-6", "value"),
        Input("intensity-1", "value"),
        Input("intensity-2", "value"),
        Input("intensity-3", "value"),
        Input("intensity-4", "value"),
        Input("intensity-5", "value"),
        Input("intensity-6", "value"),
        Input("background-1", "value"),
        Input("background-2", "value"),
        Input("background-3", "value"),
        Input("background-4", "value"),
        Input("background-5", "value"),
        Input("background-6", "value"),
        Input("cif-visibility-store", "data")
    ],
    State("cif-store", "data"),
    State("cif-order-store", "data"),
    State("upload-xy", "filename")
)
def update_xrd_plot(xy_data, opacity, exp_intensity, xrange,
                    a1, a2, a3, a4, a5, a6,
                    b1, b2, b3, b4, b5, b6,
                    c1, c2, c3, c4, c5, c6,
                    alpha1, alpha2, alpha3, alpha4, alpha5, alpha6,
                    beta1, beta2, beta3, beta4, beta5, beta6,
                    gamma1, gamma2, gamma3, gamma4, gamma5, gamma6,
                    scale1, scale2, scale3, scale4, scale5, scale6,
                    intensity1, intensity2, intensity3, intensity4, intensity5, intensity6,
                    background1, background2, background3, background4, background5, background6,
                    visibility_state,
                    cif_data, cif_order, xy_filename):

    file_names = cif_order if cif_order else []
    
    # Parse experimental data first (before checking cif_data)
    exp_data = None  # Default to None if xy_data is not provided
    xrange_min, xrange_max = xrange
    
    # Check if xy_data is not None or empty
    if xy_data:
        try:
            # Manually parse the JSON string
            parsed_data = json.loads(xy_data)

            # Create DataFrame from the parsed data
            exp_data = pd.DataFrame(parsed_data['data'], columns=parsed_data['columns'], index=parsed_data['index'])
            # Scale experimental intensity
            if exp_intensity is not None and exp_data is not None:
                exp_data['intensity'] = exp_data['intensity'] * (exp_intensity / 100)

            # Filter experimental data based on xrange
            col_candidates = ['two_theta', 'x', 'angle']
            col = next((c for c in col_candidates if c in exp_data.columns), exp_data.columns[0])
            exp_data = exp_data[(exp_data[col] >= xrange_min) & (exp_data[col] <= xrange_max)]

        except ValueError as e:
            exp_data = None

    # If no CIF data, but we have experimental data, plot just that
    if cif_data is None or len(file_names) == 0:
        if exp_data is not None:
            fig = plot_xrd([], [], "CuKa", experimental_data=exp_data, opacity=opacity, exp_filename=xy_filename, intensity_values=[])
            fig.update_layout(
                yaxis=dict(
                    range=[0, 105],
                    dtick=10,
                    showgrid=False
                ),
                legend=dict(borderwidth=0)
            )
            return fig
        else:
            return {}
    
    patterns = []
    titles = []
    num_files = len(file_names)
    a_vals = [a1, a2, a3, a4, a5, a6]
    b_vals = [b1, b2, b3, b4, b5, b6]
    c_vals = [c1, c2, c3, c4, c5, c6]
    alpha_vals = [alpha1, alpha2, alpha3, alpha4, alpha5, alpha6]
    beta_vals = [beta1, beta2, beta3, beta4, beta5, beta6]
    gamma_vals = [gamma1, gamma2, gamma3, gamma4, gamma5, gamma6]
    scale_vals = [scale1, scale2, scale3, scale4, scale5, scale6]
    intensity_vals = [intensity1, intensity2, intensity3, intensity4, intensity5, intensity6]
    background_vals = [background1, background2, background3, background4, background5, background6]

    for i in range(num_files):
        file_name = file_names[i]
        
        # Check if this CIF should be visible
        if visibility_state and file_name in visibility_state and not visibility_state[file_name]:
            continue
        
        try:
            structure = parse_cif(cif_data[file_name])
            # structure = normalize_structure(structure)
        except Exception as e:
            print("Error parsing CIF for", file_name, ":", e)
            continue
        try:
            scale_factor = 1 + (scale_vals[i] / 100) if scale_vals[i] is not None else 1
            new_a = a_vals[i] * scale_factor
            new_b = b_vals[i] * scale_factor
            new_c = c_vals[i] * scale_factor
            new_alpha = alpha_vals[i]
            new_beta = beta_vals[i]
            new_gamma = gamma_vals[i]
            new_lattice = structure.lattice.from_parameters(new_a, new_b, new_c, new_alpha, new_beta, new_gamma)
            # Rebuild structure preserving all site occupancies
            new_structure = Structure(
                new_lattice,
                [site.species for site in structure.sites],
                [site.frac_coords for site in structure.sites],
                coords_are_cartesian=False
            )
        except Exception as e:
            print("Error updating lattice for", file_name, ":", e)
            new_structure = structure

        calculator = XRDCalculator(wavelength="CuKa")
        try:
            pattern = calculator.get_pattern(new_structure, two_theta_range=(xrange_min, xrange_max))
        except Exception as e:
            print("Error in XRD calculation for", file_name, ":", e)
            continue

        # Work on a fresh copy of the original intensities
        orig_y = list(pattern.y)
        # Apply intensity scaling (per CIF)
        if intensity_vals[i] is not None and intensity_vals[i] != 100:
            scaled_y = [val * (intensity_vals[i] / 100) for val in orig_y]
        else:
            scaled_y = orig_y
        # Add the background offset (non-cumulatively)
        if background_vals[i] is not None and background_vals[i] > 0:
            new_y = [val + background_vals[i] for val in scaled_y]
        else:
            new_y = scaled_y
        pattern.y = new_y

        patterns.append(pattern)
        titles.append(file_name)
    
    # Prepare intensity values for composition calculation (only for visible CIFs)
    active_intensities = []
    for i in range(num_files):
        file_name = file_names[i]
        # Check if this CIF is visible
        is_visible = not (visibility_state and file_name in visibility_state and not visibility_state[file_name])
        if is_visible and intensity_vals[i] is not None:
            active_intensities.append(intensity_vals[i])
        elif is_visible:
            active_intensities.append(100)
    
    if not active_intensities:  # If all are None or hidden, use empty list
        active_intensities = []

    fig = plot_xrd(patterns, titles, "CuKa", experimental_data=exp_data, opacity=opacity, exp_filename=xy_filename, intensity_values=active_intensities)
    
    max_y_list = [max(pattern.y) for pattern in patterns if pattern.y is not None and len(pattern.y) > 0]
    max_y = max(max_y_list) if max_y_list else 100
    fig.update_layout(
        yaxis=dict(
            range=[0, max(105, max_y + 5)],
            dtick=10,
            showgrid=False
        ),
        legend=dict(borderwidth=0)
    )
    return fig

# ------------------------------------------------------------------
# Legend Click Callback (Toggle trace visibility)
# ------------------------------------------------------------------
@app.callback(
    Output("xrd-plot", "figure", allow_duplicate=True),
    Input("xrd-plot", "clickData"),
    State("xrd-plot", "figure"),
    prevent_initial_call=True
)
def toggle_trace_visibility(click_data, figure):
    if not click_data or not figure:
        return figure
    
    try:
        # Get the trace name from the clicked legend item
        curve_number = click_data.get('points', [{}])[0].get('curveNumber')
        if curve_number is None:
            return figure
        
        # Create a copy of the figure to modify
        fig = go.Figure(figure)
        
        # Toggle the visible property of the clicked trace
        # visible can be True, False, or "legendonly"
        if curve_number < len(fig.data):
            current_visible = fig.data[curve_number].visible
            # Toggle between True and False (or "legendonly")
            if current_visible is True or current_visible is None:
                fig.data[curve_number].visible = False
            else:
                fig.data[curve_number].visible = True
        
        return fig
    except Exception as e:
        print("Error in toggle_trace_visibility:", e)
        return figure

# ------------------------------------------------------------------
# Download Link Callback
# ------------------------------------------------------------------
@app.callback(
    Output("download-link", "href"),
    Input("xrd-plot", "figure")
)
def update_download_link(figure):
    if not figure:
        return ""
    try:
        
        fig = go.Figure(figure)
        fig.update_layout(
            width=1800,
            height=400,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=14),
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True,
            legend=dict(borderwidth=0)
        )
        pio.kaleido.scope.mathjax = None
        img_bytes = pio.to_image(
            fig,
            format="png",
            scale=2,
            engine="kaleido",
            width=1800,
            height=400,
            validate=False
        )
        b64_str = base64.b64encode(img_bytes).decode("ascii")
        href = f"data:image/png;base64,{b64_str}"
        return href
    except Exception as e:
        print("Error in generating download link:", e)
        return ""