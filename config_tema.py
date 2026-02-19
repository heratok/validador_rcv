"""
Configuración de tema pastel para el dashboard.
Colores suaves que no saturan la vista.
"""

def aplicar_tema_pastel():
    """Aplica un tema pastel suave y profesional a toda la aplicación"""
    return """
        <style>
        /* ===== TEMA PASTEL PROFESIONAL ===== */
        
        /* Importar fuente Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Fondo principal - Gradiente pastel muy suave */
        .stApp {
            background: linear-gradient(135deg, #fef6f0 0%, #f0f4ff 100%);
            color: #2d3748;
        }
        
        /* Tabs - Pasteles suaves */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff;
            gap: 12px;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f8f9fa;
            color: #64748b;
            border-radius: 10px;
            padding: 14px 28px;
            font-weight: 600;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e8f0fe;
            color: #5b7bb4;
            border-color: #a8c5f0;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #a8c5f0 0%, #c5b8e0 100%);
            color: #2d3748 !important;
            border-color: #8fa9d6;
            box-shadow: 0 3px 12px rgba(168, 197, 240, 0.3);
        }
        
        /* Títulos - Color suave */
        h1, h2, h3, h4, h5, h6 {
            color: #374151 !important;
            font-weight: 700;
        }
        h1 {
            color: #1f2937 !important;
        }
        
        /* Mensajes - Colores pastel */
        .stAlert {
            border-radius: 12px;
            padding: 16px;
            border-left: 5px solid;
            font-weight: 500;
        }
        [data-baseweb="notification"][kind="info"] {
            background-color: #e8f4fd;
            border-left-color: #7eb3d6;
            color: #1e5a7d;
        }
        [data-baseweb="notification"][kind="success"] {
            background-color: #e6f7ed;
            border-left-color: #81c995;
            color: #1e5a2f;
        }
        [data-baseweb="notification"][kind="warning"] {
            background-color: #fff8e6;
            border-left-color: #f0c674;
            color: #7d5a1e;
        }
        [data-baseweb="notification"][kind="error"] {
            background-color: #fee;
            border-left-color: #f5a3a3;
            color: #7d1e1e;
        }
        
        /* Botones - Pasteles suaves */
        .stButton button {
            background: linear-gradient(135deg, #a8c5f0 0%, #c5b8e0 100%);
            color: #2d3748;
            border: none;
            border-radius: 10px;
            padding: 14px 28px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(168, 197, 240, 0.25);
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #8fa9d6 0%, #b09cd0 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(168, 197, 240, 0.4);
        }
        .stButton button:disabled {
            background: #e5e7eb;
            color: #9ca3af;
            box-shadow: none;
        }
        
        /* Download buttons - Verde pastel */
        .stDownloadButton button {
            background: linear-gradient(135deg, #a8d5ba 0%, #c5e8d7 100%);
            color: #2d3748;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            box-shadow: 0 3px 10px rgba(168, 213, 186, 0.25);
        }
        .stDownloadButton button:hover {
            background: linear-gradient(135deg, #8fc19f 0%, #add4bf 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(168, 213, 186, 0.4);
        }
        
        /* Inputs - Fondo blanco suave */
        .stTextInput input, .stNumberInput input, .stSelectbox select {
            background-color: #ffffff;
            color: #2d3748;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            padding: 12px;
            transition: all 0.2s ease;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #a8c5f0;
            box-shadow: 0 0 0 3px rgba(168, 197, 240, 0.15);
            outline: none;
        }
        
        /* File uploader - Pastel suave */
        [data-testid="stFileUploader"] {
            background-color: #ffffff;
            border: 2px dashed #d1d5db;
            border-radius: 15px;
            padding: 25px;
            transition: all 0.3s ease;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #a8c5f0;
            background-color: #fafbfc;
            box-shadow: 0 2px 10px rgba(168, 197, 240, 0.1);
        }
        
        /* Spinner - Color pastel */
        .stSpinner > div {
            border-top-color: #a8c5f0 !important;
        }
        
        /* Divider - Línea suave */
        hr {
            border-color: #e5e7eb;
            opacity: 0.5;
        }
        
        /* Caption text - Gris suave */
        .stCaption {
            color: #6b7280 !important;
            font-size: 0.9em;
        }
        
        /* Markdown - Mejorar legibilidad */
        .stMarkdown {
            color: #374151;
        }
        
        /* Containers y columnas */
        .element-container {
            transition: all 0.2s ease;
        }
        
        /* Scrollbar personalizada (opcional) */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e0;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #a8c5f0;
        }
        </style>
    """
