import warnings
warnings.filterwarnings("ignore")

import os
import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm
from shapely.geometry import Point
import json

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

# Inicializar la aplicación Dash con supresión de excepciones de callback
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Configuración del layout con pestañas
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Análisis de la Red de Oficinas del Fondo Nacional del Ahorro", 
                   style={'color': 'white', 'marginBottom': '10px'}),
            html.P("Dashboard interactivo - Distribución territorial de oficinas en Colombia", 
                  style={'color': 'white', 'marginBottom': '0px', 'fontSize': '18px'})
        ], style={'maxWidth': '1200px', 'margin': '0 auto'})
    ], style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              'padding': '2rem 0', 'marginBottom': '2rem'}),
    
    # Pestañas
    dcc.Tabs(id="tabs", value='tab-contexto', children=[
        dcc.Tab(label='📋 Contexto y Metodología', value='tab-contexto'),
        dcc.Tab(label='📊 Análisis Visual', value='tab-analisis'),
        dcc.Tab(label='📈 Conclusiones', value='tab-conclusiones'),
    ], style={'fontFamily': 'Arial', 'fontWeight': 'bold'}),
    
    html.Div(id='tabs-content')
], style={'fontFamily': 'Arial, sans-serif', 'minHeight': '100vh', 'backgroundColor': '#f8f9fa'})

# Contenido de la pestaña de Contexto
contexto_content = html.Div([
    html.Div([
        html.Div([
            html.H2("Contexto del Estudio", style={'color': '#2c3e50', 'marginBottom': '20px', 'textAlign': 'center'}),
            html.P([
                "El presente informe analiza la estructura y distribución de la red de oficinas del ",
                html.Strong("Fondo Nacional del Ahorro (FNA)"), 
                ", institución de carácter oficial que cumple una función fundamental en el sistema de ahorro y crédito para vivienda en Colombia. Los datos utilizados en este estudio, actualizados al ",
                html.Strong("25 de agosto de 2025"), 
                ", fueron proporcionados oficialmente por el Fondo Nacional del Ahorro a través del portal de datos abiertos del Gobierno Colombiano en ",
                html.A("datos.gov.co", href="https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/Oficinas-Fondo-Nacional-del-Ahorro/h3sz-zqij/about_data", target="_blank"),
                "."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.P([
                "El conjunto de datos constituye un registro completo de la infraestructura física de atención al público del FNA, donde cada registro representa una ",
                html.Strong("sede u oficina operativa"), 
                " de la entidad en el territorio nacional. Esta información es de vital importancia para comprender la capacidad institucional de cobertura, el acceso a servicios financieros de vivienda por parte de la ciudadanía y la presencia territorial de una de las entidades más importantes del sector."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.P([
                "La disponibilidad de estos datos mediante la política de ",
                html.Strong("Gobierno Abierto"), 
                " implementada por el Gobierno de Colombia, refleja el compromiso del Estado con la transparencia y la rendición de cuentas, permitiendo a ciudadanos, investigadores y tomadores de decisiones realizar análisis basados en evidencia sobre la prestación de servicios públicos."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.H3("Metodología", style={'color': '#2c3e50', 'marginTop': '30px', 'marginBottom': '15px'}),
            html.Ul([
                html.Li("Fuente de datos: Portal de Datos Abiertos de Colombia (datos.gov.co)"),
                html.Li("Shapefile: Departamento Administrativo Nacional de Estadística (DANE)"),
                html.Li("Procesamiento: Python con Pandas, GeoPandas y Folium"),
                html.Li("Visualización: Dash y Plotly para interactividad")
            ], style={'lineHeight': '1.8'}),
            
            html.H3("Objetivos del Análisis", style={'color': '#2c3e50', 'marginTop': '30px', 'marginBottom': '15px'}),
            html.Ul([
                html.Li("Identificar patrones de distribución territorial de las oficinas del FNA"),
                html.Li("Analizar desigualdades regionales en la cobertura de servicios"),
                html.Li("Visualizar la concentración geográfica de la infraestructura financiera"),
                html.Li("Proporcionar insights para políticas públicas de inclusión financiera")
            ], style={'lineHeight': '1.8'})
            
        ], style={'padding': '2rem', 'backgroundColor': 'white', 'borderRadius': '10px', 
                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
    ], style={'maxWidth': '1000px', 'margin': '0 auto', 'padding': '20px'})
])

# Contenido de la pestaña de Conclusiones
conclusiones_content = html.Div([
    html.Div([
        html.Div([
            html.H2("Interpretación de los Resultados y Conclusiones", 
                   style={'color': '#2c3e50', 'marginBottom': '25px', 'textAlign': 'center'}),
            
            html.H3("Distribución de Oficinas del Fondo Nacional del Ahorro por Departamento", 
                   style={'color': '#34495e', 'marginTop': '30px', 'marginBottom': '15px'}),
            
            html.H4("Regiones con Valores Más Altos:", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Ul([
                html.Li([
                    html.Strong("Bogotá D.C. domina ampliamente"), 
                    " con 20 oficinas, concentrando el mayor número a nivel nacional."
                ]),
                html.Li([
                    html.Strong("Región Andina Central"), 
                    ": Departamentos como Cundinamarca, Antioquia y Valle del Cauca presentan 4 oficinas cada uno, mostrando una presencia significativa."
                ]),
                html.Li([
                    html.Strong("Zonas Intermedias"), 
                    ": Tolima, Santander y Nariño tienen 3 oficinas cada uno, indicando una cobertura media-alta."
                ])
            ], style={'lineHeight': '1.8', 'marginBottom': '20px'}),
            
            html.H4("Desigualdades Territoriales Evidentes:", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Ul([
                html.Li([
                    html.Strong("Disparidad Extrema"), 
                    ": Bogotá tiene 20 veces más oficinas que la mayoría de departamentos (que solo tienen 1)."
                ]),
                html.Li([
                    html.Strong("Centralismo Marcado"), 
                    ": La región central (Andina) concentra la mayoría de oficinas, mientras que:"
                ]),
                html.Ul([
                    html.Li("Región Caribe: Ningún departamento supera las 2 oficinas"),
                    html.Li("Región Pacífica: Chocó y Cauca solo tienen 1 oficina cada uno"),
                    html.Li("Región Amazónica: Amazonas, Guainía, Guaviare, Vaupés tienen solo 1 oficina para vastos territorios"),
                    html.Li("Región Orinoquía: Arauca, Casanare, Vichada con apenas 1 oficina cada uno")
                ], style={'marginLeft': '20px', 'marginTop': '10px'})
            ], style={'lineHeight': '1.8', 'marginBottom': '20px'}),
            
            html.H4("Factores Explicativos de las Diferencias:", style={'color': '#2c3e50', 'marginTop': '20px'}),
            
            html.H5("Factores Demográficos y Económicos:", style={'color': '#34495e', 'marginTop': '15px'}),
            html.Ul([
                html.Li("Densidad Poblacional: Bogotá y departamentos andinos tienen mayor población"),
                html.Li("Desarrollo Económico: Regiones con mayor actividad económica demandan más servicios financieros"),
                html.Li("Urbanización: Áreas urbanas concentran mayor demanda de créditos de vivienda")
            ], style={'lineHeight': '1.8', 'marginBottom': '15px'}),
            
            html.H5("Factores Geográficos y Logísticos:", style={'color': '#34495e', 'marginTop': '15px'}),
            html.Ul([
                html.Li("Accesibilidad: Departamentos remotos (Amazonas, Guainía) presentan desafíos de conectividad"),
                html.Li("Extensión Territorial: Departamentos grandes con baja densidad (Vichada, Guaviare) tienen menor cobertura")
            ], style={'lineHeight': '1.8', 'marginBottom': '15px'}),
            
            html.H5("Factores Institucionales y Históricos:", style={'color': '#34495e', 'marginTop': '15px'}),
            html.Ul([
                html.Li("Enfoque de Mercado: Priorización de zonas con mayor potencial of cartera"),
                html.Li("Infraestructura Existente: Limitaciones en instalación de oficinas en zonas periféricas")
            ], style={'lineHeight': '1.8', 'marginBottom': '20px'}),
            
            html.Div([
                html.H4("Conclusión Principal", style={'color': '#2c3e50', 'textAlign': 'center'}),
                html.P([
                    "La distribución refleja patrones históricos de desarrollo desigual en Colombia, donde las regiones centrales concentran la infraestructura financiera mientras las periféricas enfrentan limitaciones de acceso."
                ], style={'textAlign': 'center', 'fontStyle': 'italic', 'fontSize': '18px', 
                         'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
            ], style={'marginTop': '30px', 'marginBottom': '30px'}),
            
            html.H3("La Georreferenciación como Herramienta Clave para el Análisis Social", 
                   style={'color': '#34495e', 'marginTop': '40px', 'marginBottom': '15px'}),
            
            html.P([
                "El análisis georreferenciado de la distribución de oficinas del Fondo Nacional del Ahorro evidencia la ",
                html.Strong("capacidad transformadora de los datos espaciales"), 
                " en estudios sociales. La visualización espacial no solo permite identificar patrones geográficos de concentración y exclusión, sino que ",
                html.Strong("revela dimensiones críticas del desarrollo territorial"), 
                " que pasarían desapercibidas en análisis tabulares convencionales."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.P([
                "La georreferenciación ",
                html.Strong("materializa las desigualdades"), 
                ", transformando datos abstractos en realidades tangibles: muestra cómo el centralismo bogotano se impone sobre las periferias, cómo la región Caribe a pesar de su extensión y población mantiene una cobertura marginal, y cómo la Amazonia y Orinoquia enfrentan desafíos de inclusión financiera proporcionales a su vastedad territorial."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.P([
                "Este ejercicio demuestra que ",
                html.Strong("la geografía no es solo un contenedor de fenómenos sociales, sino un factor activo"), 
                " que configura oportunidades de acceso. La disposición espacial de la infraestructura financiera refleja y, a la vez, reproduce dinámicas de desarrollo desigual, haciendo evidente la ",
                html.Strong("necesidad de políticas públicas con enfoque territorial diferenciado"), 
                "."
            ], style={'textAlign': 'justify', 'lineHeight': '1.6', 'marginBottom': '15px'}),
            
            html.H4("Aportes de la Georreferenciación para la Equidad", style={'color': '#2c3e50', 'marginTop': '25px'}),
            html.Ul([
                html.Li("Identificar brechas de cobertura con precisión"),
                html.Li("Priorizar inversiones en territorios históricamente marginados"),
                html.Li("Diseñar estrategias adaptadas a las realidades regionales"),
                html.Li("Evaluar impactos de políticas con dimensión espacial")
            ], style={'lineHeight': '1.8', 'marginBottom': '20px'})
            
        ], style={'padding': '2rem', 'backgroundColor': 'white', 'borderRadius': '10px', 
                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
    ], style={'maxWidth': '1000px', 'margin': '0 auto', 'padding': '20px'})
])

# Callback para las pestañas
@callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-contexto':
        return contexto_content
    elif tab == 'tab-conclusiones':
        return conclusiones_content
    elif tab == 'tab-analisis':
        return html.Div([
            # Contenido principal del análisis
            html.Div([
                # Primera fila: Estadísticas clave
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div(id="total-oficinas", style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'color': '#2c3e50'}),
                            html.Div("Total Oficinas", style={'fontSize': '1rem', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 
                                 'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '24%', 'display': 'inline-block', 'margin': '0.5%'}),
                    
                    html.Div([
                        html.Div([
                            html.Div(id="total-departamentos", style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'color': '#2c3e50'}),
                            html.Div("Departamentos con Cobertura", style={'fontSize': '1rem', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 
                                 'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '24%', 'display': 'inline-block', 'margin': '0.5%'}),
                    
                    html.Div([
                        html.Div([
                            html.Div(id="min-oficinas", style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'color': '#2c3e50'}),
                            html.Div("Mín. Oficinas por Depto", style={'fontSize': '1rem', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 
                                 'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '24%', 'display': 'inline-block', 'margin': '0.5%'}),
                    
                    html.Div([
                        html.Div([
                            html.Div(id="max-oficinas", style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'color': '#2c3e50'}),
                            html.Div("Máx. Oficinas por Depto", style={'fontSize': '1rem', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 
                                 'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '24%', 'display': 'inline-block', 'margin': '0.5%'})
                ], style={'marginBottom': '2rem', 'textAlign': 'center', 'display': 'flex', 'justifyContent': 'space-between'}),
                
                # Segunda fila: Mapa y controles AL LADO
                html.Div([
                    # Columna del mapa
                    html.Div([
                        html.Div([
                            html.H4("Distribución Geográfica de Oficinas", 
                                   style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '1rem', 
                                         'margin': '0', 'borderRadius': '10px 10px 0 0'}),
                            html.Div([
                                html.Iframe(id='folium-map', style={'width': '100%', 'height': '500px', 'border': 'none'})
                            ], style={'padding': '1rem'})
                        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
                    
                    # Columna de controles (al lado del mapa)
                    html.Div([
                        html.Div([
                            html.H4("Controles de Visualización", 
                                   style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '1rem', 
                                         'margin': '0', 'borderRadius': '10px 10px 0 0'}),
                            html.Div([
                                html.Label("Tipo de Mapa:", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'marginTop': '5px'}),
                                dcc.Dropdown(
                                    id='map-type-selector',
                                    options=[
                                        {'label': '🎨 Mapa Temático (Escala de Colores)', 'value': 'thematic'},
                                        {'label': '🔵 Mapa Temático (Escala de Azules)', 'value': 'blues'}
                                    ],
                                    value='thematic',
                                    style={'marginBottom': '15px'}
                                ),
                                
                                html.Label("Filtrar por Número de Oficinas:", 
                                         style={'fontWeight': 'bold', 'display': 'block', 'marginTop': '20px', 'marginBottom': '15px'}),
                                dcc.RangeSlider(
                                    id='office-slider',
                                    min=1,
                                    max=20,
                                    step=1,
                                    value=[1, 20],
                                    marks={1: '1', 2: '2', 3: '3', 4: '4', 20: '20'},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                ),
                                
                                html.Label("Filtrar por Región:", 
                                         style={'fontWeight': 'bold', 'display': 'block', 'marginTop': '25px', 'marginBottom': '8px'}),
                                dcc.Dropdown(
                                    id='region-filter',
                                    multi=True,
                                    placeholder="Seleccione regiones...",
                                    style={'marginBottom': '20px'}
                                ),
                                
                                html.Button("🔄 Resetear Filtros", id="reset-filters", 
                                           style={'width': '100%', 'padding': '12px', 
                                                 'border': '1px solid #007bff', 'backgroundColor': 'transparent',
                                                 'color': '#007bff', 'borderRadius': '5px', 'cursor': 'pointer',
                                                 'fontWeight': 'bold', 'marginTop': '10px', 'transition': 'all 0.3s ease'},
                                           n_clicks=0)
                            ], style={'padding': '1.5rem'})
                        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
                ], style={'marginBottom': '2rem', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}),
                
                # Tercera fila: Gráficos (al lado) - CORREGIDO
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Top 7 Departamentos con Más Oficinas", 
                                   style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '1rem', 
                                         'margin': '0', 'borderRadius': '10px 10px 0 0'}),
                            dcc.Graph(id='top-departments-chart')
                        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
                    
                    html.Div([
                        html.Div([
                            html.H4("Distribución por Número de Oficinas", 
                                   style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '1rem', 
                                         'margin': '0', 'borderRadius': '10px 10px 0 0'}),
                            dcc.Graph(id='distribution-chart')
                        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'height': '100%'})
                    ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
                ], style={'marginBottom': '2rem'}),  # ELIMINADO display: flex
                
                # Cuarta fila: Tabla de datos mejorada
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("📋 Detalle de Oficinas por Departamento", 
                                   style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '1rem', 
                                         'margin': '0', 'borderRadius': '10px 10px 0 0'}),
                            html.Div(id='data-table-container', style={'padding': '1rem', 'maxHeight': '500px', 'overflowY': 'auto'})
                        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                                 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                    ], style={'width': '100%', 'padding': '10px'})
                ])
            ], style={'maxWidth': '1200px', 'margin': '0 auto', 'backgroundColor': '#f8f9fa', 'padding': '20px'})
        ])

def load_and_process_data():
    """Cargar y procesar los datos una vez al inicio"""
    try:
        # Ruta CORREGIDA - incluye la subcarpeta MGN2021_DPTO_POLITICO
        shapefile_path = "data/MGN2021_DPTO_POLITICO/MGN_DPTO_POLITICO.shp"
        data = gpd.read_file(shapefile_path, encoding='utf-8')
        
        # Cargar datos de oficinas
        df = pd.read_csv("data/Oficinas_Fondo_Nacional_del_Ahorro_20250906.csv")
        
        # Procesamiento de datos (similar a tu análisis original)
        df["departamentos"] = df["departamentos"].str.upper()
        df["departamentos"].replace(to_replace="HONDA", value="TOLIMA", inplace=True)
        
        # Crear DataFrame para unión espacial
        conteo_oficinas = df['departamentos'].value_counts().reset_index()
        conteo_oficinas.columns = ['departamento', 'cantidad_oficinas']
        
        # Estandarización de caracteres en shapefile
        caracteres_mal = ['Á', 'É', 'Í', 'Ó', 'Ú']  
        caracteres_bien = ['A', 'E', 'I', 'O', 'U'] 

        data["DPTO_CNMBR_NORM"] = data["DPTO_CNMBR"].copy()
        for j in range(len(caracteres_mal)):  
            data["DPTO_CNMBR_NORM"] = data["DPTO_CNMBR_NORM"].str.replace(caracteres_mal[j], caracteres_bien[j])
        
        # Corrección de nombres en el dataset
        mapeo_nombres = {
            'BOGOTA  D.C.': 'BOGOTA, D.C.',
            'BOGOTA D.C.': 'BOGOTA, D.C.',
            'GUAJIRA': 'LA GUAJIRA',
            'SAN ANDRES': 'ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA',
            'NORTE DE SANTADER': 'NORTE DE SANTANDER', 
            'GUANIA': 'GUAINIA',
            'VALLE': 'VALLE DEL CAUCA'
        }
        
        conteo_oficinas['departamento_norm'] = conteo_oficinas['departamento'].replace(mapeo_nombres)
        
        # Unir datos
        data_unida = data.merge(conteo_oficinas, 
                               left_on='DPTO_CNMBR_NORM', 
                               right_on='departamento_norm', 
                               how='left')
        
        data_unida['cantidad_oficinas'] = data_unida['cantidad_oficinas'].fillna(0)
        
        return data_unida, df
        
    except Exception as e:
        print(f"Error cargando datos: {e}")
        # Retornar datos de ejemplo si hay error
        return create_sample_data(), pd.DataFrame()

def create_sample_data():
    """Crear datos de ejemplo si hay error con los archivos"""
    sample_data = {
        'DPTO_CNMBR': ['BOGOTA, D.C.', 'ANTIOQUIA', 'VALLE DEL CAUCA', 'CUNDINAMARCA', 
                      'SANTANDER', 'NARIÑO', 'TOLIMA', 'ATLANTICO', 'BOLIVAR', 'BOYACA'],
        'cantidad_oficinas': [20, 4, 4, 4, 3, 3, 3, 2, 2, 2],
        'geometry': [None] * 10  # Geometría vacía para evitar errores
    }
    return pd.DataFrame(sample_data)

# Cargar datos una vez al inicio
data_unida_global, df_global = load_and_process_data()

# Callbacks principales - CORREGIDO
@callback(
    [Output('folium-map', 'srcDoc'),
     Output('total-oficinas', 'children'),
     Output('total-departamentos', 'children'),
     Output('min-oficinas', 'children'),
     Output('max-oficinas', 'children'),
     Output('top-departments-chart', 'figure'),
     Output('distribution-chart', 'figure'),
     Output('data-table-container', 'children'),
     Output('region-filter', 'options')],
    [Input('map-type-selector', 'value'),
     Input('office-slider', 'value'),
     Input('region-filter', 'value'),
     Input('reset-filters', 'n_clicks')]
)
def update_dashboard(map_type, office_range, selected_regions, n_clicks):
    try:
        if data_unida_global is None or df_global is None:
            raise Exception("No se pudieron cargar los datos")
        
        # Aplicar filtros - CORREGIDO
        filtered_data = data_unida_global.copy()
        
        # Manejar caso cuando selected_regions es None o vacío
        if selected_regions:
            filtered_data = filtered_data[filtered_data['DPTO_CNMBR_NORM'].isin(selected_regions)]
        
        # Aplicar filtro de rango de oficinas
        filtered_data = filtered_data[
            (filtered_data['cantidad_oficinas'] >= office_range[0]) & 
            (filtered_data['cantidad_oficinas'] <= office_range[1])
        ]
        
        # Calcular estadísticas
        total_oficinas = int(df_global.shape[0]) if not df_global.empty else 71
        total_departamentos = len(data_unida_global[data_unida_global['cantidad_oficinas'] > 0])
        max_oficinas = int(data_unida_global['cantidad_oficinas'].max())
        min_oficinas = int(data_unida_global[data_unida_global['cantidad_oficinas'] > 0]['cantidad_oficinas'].min())
        
        # Crear componentes
        mapa = create_folium_map(data_unida_global, filtered_data, map_type)
        map_html = mapa._repr_html_() if mapa else "<div>Error creando mapa</div>"
        
        top_chart = create_top_departments_chart(data_unida_global)
        dist_chart = create_distribution_chart(data_unida_global)
        table = create_data_table(data_unida_global)
        
        # Opciones para el filtro de región
        region_options = [{'label': depto, 'value': depto} 
                        for depto in sorted(data_unida_global['DPTO_CNMBR_NORM'].unique())]

        return (map_html, total_oficinas, total_departamentos, min_oficinas, 
                max_oficinas, top_chart, dist_chart, table, region_options)
    
    except Exception as e:
        print(f"Error en update_dashboard: {e}")
        # Retornar valores por defecto en caso de error
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error cargando los datos", 
                               xref="paper", yref="paper", x=0.5, y=0.5, 
                               showarrow=False)
        
        region_options = [{'label': 'Error', 'value': 'error'}]
        
        return ("<div style='padding: 20px; text-align: center;'><h3>Error cargando los datos</h3></div>", 
                "71", "33", "1", "20", empty_fig, empty_fig, 
                html.Div("Error cargando datos"), region_options)

def create_folium_map(all_data, filtered_data, map_type):
    """Crear mapa Folium con sistema de dos capas - CORREGIDO"""
    mapa = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    
    # PRIMERA CAPA: Todos los departamentos en gris claro
    def base_style_function(feature):
        return {
            'fillColor': '#F7F7F7FF',
            'color': 'black',  
            'weight': 1.1,
            'fillOpacity': 0.6
        }
    
    folium.GeoJson(
        all_data,
        style_function=base_style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['DPTO_CNMBR', 'cantidad_oficinas'],
            aliases=['Departamento: ', 'Oficinas: '],
            localize=True
        )
    ).add_to(mapa)
    
    # SEGUNDA CAPA: Solo departamentos filtrados con colores según el tipo de mapa
    if not filtered_data.empty and 'geometry' in filtered_data.columns and not filtered_data['geometry'].isnull().all():
        if map_type == 'thematic':
            # Mapa temático original con colores variados
            colores_ylorrd_compacta = ['#7CFC00', '#FFFF00', '#FFA500', '#FF0000', '#800080']
            valores_unicos = sorted(filtered_data['cantidad_oficinas'].unique())
            color_dict = {valor: colores_ylorrd_compacta[i % len(colores_ylorrd_compacta)] 
                         for i, valor in enumerate(valores_unicos)}
            
            def thematic_style_function(feature):
                cantidad = feature['properties']['cantidad_oficinas']
                return {
                    'fillColor': color_dict.get(cantidad, '#CCCCCC'),
                    'color': 'black',  
                    'weight': 1.1,
                    'fillOpacity': 0.6
                }
            
            style_function = thematic_style_function
            
            # Leyenda para mapa temático
            legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; 
                 background-color: white; border:2px solid grey; z-index:9999;
                 font-size:10px; padding: 10px;">
                 <b>Cantidad de Oficinas</b><br>
            '''
            
            for i, valor in enumerate(valores_unicos):
                color = colores_ylorrd_compacta[i % len(colores_ylorrd_compacta)]
                legend_html += f'''
                <i style="background:{color}; width: 12px; height: 12px; 
                display: inline-block; margin-right: 5px; opacity: 0.8; border: 1px solid black;"></i>
                {valor} oficina(s)<br>
                '''
            
            legend_html += '''
                <i style="background:#F7F7F7FF; width: 12px; height: 12px; 
                display: inline-block; margin-right: 5px; opacity: 0.8; border: 1px solid black;"></i>
                Otros departamentos<br>
            </div>
            '''
            
        else:  # Mapa con escala de azules
            colores_azules = ["#9FBFFFFF", "#3E7DFBFF", "#0000FFE1", "#000080", '#FFFF00FF']
            valores_unicos = sorted(filtered_data['cantidad_oficinas'].unique())
            color_dict = {valor: colores_azules[i % len(colores_azules)] for i, valor in enumerate(valores_unicos)}
            
            def blues_style_function(feature):
                cantidad = feature['properties']['cantidad_oficinas']
                return {
                    'fillColor': color_dict.get(cantidad, '#CCCCCC'),
                    'color': 'black',  
                    'weight': 1.1,
                    'fillOpacity': 0.6
                }
            
            style_function = blues_style_function
            
            # Leyenda para mapa azul
            legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; 
                 background-color: white; border:2px solid grey; z-index:9999;
                 font-size:10px; padding: 10px;">
                 <b>Cantidad de Oficinas</b><br>
            '''
            
            for i, valor in enumerate(valores_unicos):
                color = colores_azules[i % len(colores_azules)]
                legend_html += f'''
                <i style="background:{color}; width: 12px; height: 12px; 
                display: inline-block; margin-right: 5px; opacity: 0.8; border: 1px solid black;"></i>
                {valor} oficina(s)<br>
                '''
            
            legend_html += '''
                <i style="background:#F7F7F7FF; width: 12px; height: 12px; 
                display: inline-block; margin-right: 5px; opacity: 0.8; border: 1px solid black;"></i>
                Otros departamentos<br>
            </div>
            '''
        
        # Añadir la segunda capa con los datos filtrados
        folium.GeoJson(
            filtered_data,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['DPTO_CNMBR', 'cantidad_oficinas'],
                aliases=['Departamento: ', 'Oficinas: '],
                localize=True
            )
        ).add_to(mapa)
        
        # Añadir leyenda
        mapa.get_root().html.add_child(folium.Element(legend_html))
    
    return mapa

def get_heatmap_color(value):
    """Obtener color para mapa de calor"""
    if value == 0:
        return '#F7F7F7'
    elif value <= 1:
        return '#B0E57C'
    elif value <= 2:
        return '#FFD700'
    elif value <= 3:
        return '#FF8C00'
    else:
        return '#FF4500'

def create_top_departments_chart(data):
    """Crear gráfico de top 7 departamentos"""
    top_data = data.nlargest(7, 'cantidad_oficinas')  # Cambiado de 10 a 7
    
    # Colores específicos para cada categoría
    color_map = {
        20: '#800080',  # Morado para 20 oficinas
        4: '#FF0000',   # Rojo para 4 oficinas
        3: '#FFA500',   # Naranja para 3 oficinas
        2: '#FFFF00',   # Amarillo para 2 oficinas
        1: '#7CFC00'    # Verde para 1 oficina
    }
    
    # Asignar colores basados en la cantidad de oficinas
    colors = [color_map.get(x, '#CCCCCC') for x in top_data['cantidad_oficinas']]
    
    fig = px.bar(
        top_data,
        y='DPTO_CNMBR',
        x='cantidad_oficinas',
        orientation='h',
        title='',
        labels={'cantidad_oficinas': 'Número de Oficinas', 'DPTO_CNMBR': 'Departamento'}
    )
    
    fig.update_traces(
        marker_color=colors,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )
    
    return fig

def create_distribution_chart(data):
    """Crear gráfico de distribución"""
    dist_data = data['cantidad_oficinas'].value_counts().sort_index()
    
    # Colores específicos para el gráfico de torta
    colores_torta = ['#7CFC00', '#FFFF00', '#FFA500', '#FF0000', '#800080']
    
    fig = px.pie(
        values=dist_data.values,
        names=[f"{int(x)} oficina(s)" for x in dist_data.index],
        title='',
        color_discrete_sequence=colores_torta
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig

def create_data_table(data):
    """Crear tabla de datos mejorada estéticamente"""
    table_data = data[['DPTO_CNMBR', 'cantidad_oficinas']].sort_values('cantidad_oficinas', ascending=False)
    
    # Crear filas de la tabla con mejor estilo
    rows = []
    for idx, row in table_data.iterrows():
        # Asignar colores basados en el número de oficinas
        if row['cantidad_oficinas'] >= 4:
            row_style = {'backgroundColor': '#e8f5e8', 'borderBottom': '1px solid #ddd'}
            badge_color = '#28a745'
        elif row['cantidad_oficinas'] == 3:
            row_style = {'backgroundColor': '#fff3cd', 'borderBottom': '1px solid #ddd'}
            badge_color = '#ffc107'
        elif row['cantidad_oficinas'] == 2:
            row_style = {'backgroundColor': '#ffeaa7', 'borderBottom': '1px solid #ddd'}
            badge_color = '#fd7e14'
        else:
            row_style = {'backgroundColor': '#f8f9fa', 'borderBottom': '1px solid #ddd'}
            badge_color = '#6c757d'
        
        badge_style = {
            'backgroundColor': badge_color,
            'color': 'white',
            'padding': '5px 10px',
            'borderRadius': '15px',
            'fontSize': '12px',
            'fontWeight': 'bold',
            'minWidth': '40px',
            'textAlign': 'center',
            'display': 'inline-block'
        }
        
        rows.append(html.Tr([
            html.Td(row['DPTO_CNMBR'], style={'padding': '12px', 'fontWeight': '500'}),
            html.Td(
                html.Span(f"{int(row['cantidad_oficinas'])}", style=badge_style),
                style={'padding': '12px', 'textAlign': 'center'}
            )
        ], style=row_style))
    
    table = html.Table([
        html.Thead([
            html.Tr([
                html.Th('Departamento', style={'padding': '15px', 'textAlign': 'left', 'borderBottom': '2px solid #2c3e50', 
                                             'backgroundColor': '#34495e', 'color': 'white', 'fontSize': '14px'}),
                html.Th('Número de Oficinas', style={'padding': '15px', 'textAlign': 'center', 'borderBottom': '2px solid #2c3e50',
                                                   'backgroundColor': '#34495e', 'color': 'white', 'fontSize': '14px'})
            ])
        ]),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontFamily': 'Arial, sans-serif'})
    
    return table

# Callback para resetear filtros
@callback(
    [Output('office-slider', 'value'),
     Output('region-filter', 'value')],
    Input('reset-filters', 'n_clicks')
)
def reset_filters(n_clicks):
    return [1, 20], []

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))