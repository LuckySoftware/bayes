import dash
from dash import dcc, html, Dash, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import pandas as pd
import base64
import io
import datetime
import pdfkit
from jinja2 import Template

# ================================================
# APP CONFIGURATION
# ================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "BayesPro Analytics"
server = app.server

# Configuración para PDF (requiere wkhtmltopdf)
PDF_CONFIG = {
    'enable-local-file-access': None,
    'quiet': ''
}

# ================================================
# COMPONENTS
# ================================================
controls = dbc.Card(
    [
        dbc.Form([
            dbc.Label("Nombre del Evento A", className="fw-bold"),
            dbc.Input(id='nombre-a', placeholder="Ej: Enfermedad", value="Evento A"),
            
            dbc.Label("Nombre del Evento B", className="fw-bold mt-3"),
            dbc.Input(id='nombre-b', placeholder="Ej: Prueba Positiva", value="Evento B"),
            
            html.Hr(),
            
            dbc.Label("Probabilidad inicial P(A)", className="fw-bold"),
            dbc.Input(id='p_a', type='number', min=0, max=1, step=0.01, value=0.02),
            dcc.Slider(id='p_a_slider', min=0, max=1, step=0.01, value=0.02,
                      marks={i/10: str(i/10) for i in range(0, 11)}),
            
            dbc.Label("Sensibilidad P(B|A)", className="fw-bold mt-3"),
            dbc.Input(id='p_b_dado_a', type='number', min=0, max=1, step=0.01, value=0.9),
            dcc.Slider(id='p_b_dado_a_slider', min=0, max=1, step=0.01, value=0.9,
                      marks={i/10: str(i/10) for i in range(0, 11)}),
            
            dbc.Label("Falsos positivos P(B|¬A)", className="fw-bold mt-3"),
            dbc.Input(id='p_b_dado_no_a', type='number', min=0, max=1, step=0.01, value=0.01),
            dcc.Slider(id='p_b_dado_no_a_slider', min=0, max=1, step=0.01, value=0.01,
                      marks={i/10: str(i/10) for i in range(0, 11)}),
            
            dbc.Button("Calcular", id="btn-calcular", color="primary", className="mt-4 w-100"),
        ]),
    ],
    body=True,
    className="shadow"
)

# ================================================
# LAYOUT
# ================================================
app.layout = dbc.Container(
    [
        dcc.Store(id='store-calculations'),
        dcc.Download(id="download-report"),
        dcc.Store(id='theme-store', data='light'),
        
        dbc.Row([
            dbc.Col(html.H1("BayesPro Analytics", className="text-center my-4"), width=12)
        ]),
        
        dbc.Row([
            dbc.Col(controls, md=4, className="mb-4"),
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(
                        [
                            dbc.Spinner(dcc.Graph(id='grafico-bayes', className="border rounded shadow")),
                            html.Div(id='resultado-detallado', className="mt-3 p-3 bg-light rounded")
                        ],
                        label="Análisis Bayesiano",
                        tab_id="tab-analisis"
                    ),
                    dbc.Tab(
                        [
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Rango de P(A):", className="fw-bold"),
                                    dcc.RangeSlider(id='rango-sensibilidad', min=0, max=1, step=0.05, 
                                                  value=[0, 1], marks={i/10: str(i/10) for i in range(0, 11)})
                                ], width=12),
                                dbc.Col(dcc.Graph(id='grafico-sensibilidad'), width=12)
                            ])
                        ],
                        label="Análisis de Sensibilidad",
                        tab_id="tab-sensibilidad"
                    )
                ], id="tabs-principales", active_tab="tab-analisis"),
                
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-file-pdf me-2"),
                        "Exportar Reporte"
                    ], id="btn-exportar", color="danger", className="mt-3 me-2"),
                    
                    dbc.Button([
                        html.I(className="fas fa-moon me-2"),
                        "Modo Oscuro"
                    ], id="btn-tema", color="secondary", className="mt-3"),
                ], className="d-flex justify-content-end")
            ], md=8)
        ]),
        
        dbc.Toast(
            "Cálculos actualizados correctamente",
            id="toast-notificacion",
            header="BayesPro",
            is_open=False,
            dismissable=True,
            icon="success",
            className="position-fixed top-0 end-0 m-3"
        )
    ],
    fluid=True,
    className="dbc p-4"
)

# ================================================
# CALLBACKS
# ================================================
# Sincronizar inputs y sliders
for param in ['p_a', 'p_b_dado_a', 'p_b_dado_no_a']:
    @callback(
        [Output(param, 'value'), Output(f'{param}_slider', 'value')],
        [Input(param, 'value'), Input(f'{param}_slider', 'value')],
        prevent_initial_call=True
    )
    def sync_values(input_val, slider_val):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == param:
            return input_val, input_val
        else:
            return slider_val, slider_val

# Callback principal combinado
@app.callback(
    [Output('store-calculations', 'data'),
     Output('grafico-bayes', 'figure'),
     Output('resultado-detallado', 'children'),
     Output('toast-notificacion', 'is_open')],
    [Input('btn-calcular', 'n_clicks'),
     Input('theme-store', 'data')],  # Añadimos el tema como input
    [State('nombre-a', 'value'),
     State('nombre-b', 'value'),
     State('p_a', 'value'),
     State('p_b_dado_a', 'value'),
     State('p_b_dado_no_a', 'value')]
)
def calcular_bayes(n_clicks, theme, nombre_a, nombre_b, p_a, p_b_dado_a, p_b_dado_no_a):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Solo actualizar si se hizo clic en calcular o si cambió el tema
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id not in ['btn-calcular', 'theme-store']:
        raise PreventUpdate
    
    # Validación de datos
    if None in [p_a, p_b_dado_a, p_b_dado_no_a]:
        raise PreventUpdate
    
    # Cálculos principales
    try:
        p_no_a = 1 - p_a
        p_b = (p_b_dado_a * p_a) + (p_b_dado_no_a * p_no_a)
        p_a_dado_b = (p_b_dado_a * p_a) / p_b if p_b != 0 else 0
        p_no_a_dado_b = 1 - p_a_dado_b
        
        # Datos para almacenar
        data = {
            'nombres': {'a': nombre_a, 'b': nombre_b},
            'valores': {
                'p_a': p_a,
                'p_b_dado_a': p_b_dado_a,
                'p_b_dado_no_a': p_b_dado_no_a,
                'p_b': p_b,
                'p_a_dado_b': p_a_dado_b
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Gráfico principal
        fig = px.bar(
            x=[f'P({nombre_a})', f'P(¬{nombre_a})', f'P({nombre_a}|{nombre_b})', f'P(¬{nombre_a}|{nombre_b})'],
            y=[p_a, p_no_a, p_a_dado_b, p_no_a_dado_b],
            color=['Prob. Previa', 'Prob. Previa', 'Prob. Posterior', 'Prob. Posterior'],
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
            labels={'x': 'Probabilidad', 'y': 'Valor'},
            title=f'Análisis Bayesiano: {nombre_a} vs {nombre_b}',
            height=400
        )
        
        # Aplicar tema
        if theme == 'dark':
            fig.update_layout(
                plot_bgcolor='#303030',
                paper_bgcolor='#303030',
                font_color='white',
                title_font_color='white'
            )
        else:
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='black',
                title_font_color='black'
            )
        
        # Resultado detallado
        resultado = dbc.Card([
            dbc.CardHeader("Resultados Bayesianos Detallados", className="fw-bold"),
            dbc.CardBody([
                html.H4(f"Probabilidad inicial P({nombre_a}): {p_a:.2%}", className="lead"),
                html.P(f"Sensibilidad P({nombre_b}|{nombre_a}): {p_b_dado_a:.2%}"),
                html.P(f"Falsos positivos P({nombre_b}|¬{nombre_a}): {p_b_dado_no_a:.2%}"),
                html.Hr(),
                html.H4(f"Probabilidad posterior P({nombre_a}|{nombre_b}) = {p_a_dado_b:.2%}", 
                       className="text-success fw-bold"),
                html.P("Probabilidad actualizada después de observar la evidencia", className="text-muted"),
                html.Hr(),
                html.P(f"P({nombre_b}) = {p_b:.2%} (Probabilidad total de la evidencia)")
            ])
        ])
        
        # Mostrar notificación solo cuando se hace clic en calcular
        show_toast = trigger_id == 'btn-calcular'
        
        return data, fig, resultado, show_toast
    
    except Exception as e:
        return dash.no_update, dash.no_update, html.Div(f"Error: {str(e)}", className="alert alert-danger"), False

# Exportar a PDF
@app.callback(
    Output("download-report", "data"),
    Input("btn-exportar", "n_clicks"),
    State("store-calculations", "data"),
    prevent_initial_call=True
)
def exportar_pdf(n_clicks, data):
    if n_clicks is None or not data:
        raise PreventUpdate
    
    try:
        # Plantilla HTML para el PDF
        template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte Bayesiano</title>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #2c3e50; }
                .card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
                .resultado { font-size: 1.2em; color: #27ae60; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Reporte Bayesiano - {{ timestamp }}</h1>
            
            <div class="card">
                <h2>Parámetros</h2>
                <p><strong>Evento A:</strong> {{ nombres.a }}</p>
                <p><strong>Evento B:</strong> {{ nombres.b }}</p>
                <p>P(A): {{ valores.p_a|float|round(4) }} ({{ (valores.p_a*100)|float|round(2) }}%)</p>
                <p>P(B|A): {{ valores.p_b_dado_a|float|round(4) }} ({{ (valores.p_b_dado_a*100)|float|round(2) }}%)</p>
                <p>P(B|¬A): {{ valores.p_b_dado_no_a|float|round(4) }} ({{ (valores.p_b_dado_no_a*100)|float|round(2) }}%)</p>
            </div>
            
            <div class="card">
                <h2>Resultados</h2>
                <p class="resultado">P(A|B) = {{ valores.p_a_dado_b|float|round(4) }} ({{ (valores.p_a_dado_b*100)|float|round(2) }}%)</p>
                <p>P(B) = {{ valores.p_b|float|round(4) }} ({{ (valores.p_b*100)|float|round(2) }}%)</p>
            </div>
        </body>
        </html>
        ''')
        
        html_content = template.render(
            nombres=data['nombres'],
            valores=data['valores'],
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Crear PDF
        pdf_bytes = pdfkit.from_string(html_content, False, configuration=PDF_CONFIG)
        
        return {
            "content": pdf_bytes,
            "filename": f"reporte_bayesiano_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "type": "application/pdf"
        }
    
    except Exception as e:
        return {"content": str(e).encode(), "filename": "error.txt", "type": "text/plain"}

# Tema oscuro/claro
@app.callback(
    [Output('theme-store', 'data'),
     Output('btn-tema', 'children')],
    [Input('btn-tema', 'n_clicks')],
    [State('theme-store', 'data')],
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    if n_clicks is None:
        raise PreventUpdate
    
    new_theme = 'dark' if current_theme == 'light' else 'light'
    icon = "fa-sun" if new_theme == 'dark' else "fa-moon"
    text = "Modo Claro" if new_theme == 'dark' else "Modo Oscuro"
    
    return new_theme, [html.I(className=f"fas {icon} me-2"), text]

# ================================================
# EJECUCIÓN
# ================================================
if __name__ == '__main__':
    app.run(debug=True)