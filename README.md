# Sistema de Análisis Bayesiano con Interfaz Web

## Resumen Ejecutivo
Aplicación integral que combina métodos estadísticos bayesianos con una interfaz web interactiva desarrollada en Dash. Permite:
- Modelado probabilístico avanzado
- Visualización dinámica de distribuciones
- Generación de reportes PDF automatizados
- Integración con flujos de trabajo de ciencia de datos

## Requisitos Técnicos
- Python 3.10+
- wkhtmltopdf 0.12.6+ (para generación de PDFs)
- Navegador web moderno

## Configuración del Entorno
```bash
# Instalar dependencias
pip install -r requirements.txt

# Instalar wkhtmltopdf (macOS)
brew install --cask wkhtmltopdf
```

## Descripción
Implementación de métodos estadísticos bayesianos para análisis de datos. Proyecto desarrollado en Python con enfoque en inferencia probabilística.

## Características Principales
- Estimación de parámetros mediante muestreo de Gibbs
- Integración con NumPy para cálculo matricial
- Visualización de resultados con Matplotlib

## Requisitos del Sistema
- Python 3.8+
- NumPy 1.21+
- Matplotlib 3.5+

## Instalación
```bash
pip install -r requirements.txt
```

## Operación de la Interfaz Web
```bash
# Iniciar servidor de desarrollo
export PATH="$PATH:/usr/local/bin/wkhtmltopdf"  # Configurar ruta para PDF
export PYTHONPATH="$PYTHONPATH:$(pwd)"  # Añadir directorio actual al PYTHONPATH
python script.py

# Acceder desde navegador:
http://localhost:8050
```

### Flujo de Trabajo Típico
1. Cargar conjunto de datos (CSV o Excel)
2. Seleccionar tipo de modelo bayesiano
3. Configurar parámetros de muestreo
4. Visualizar distribuciones a priori/posteriori
5. Exportar reporte PDF con resultados

## Requisitos Adicionales
Para generación de PDFs:
```bash
# Verificar instalación de wkhtmltopdf
wkhtmltopdf --version

# Configurar permisos (macOS)
sudo chmod +x /usr/local/bin/wkhtmltopdf
```

## Arquitectura del Sistema
```
.
├── script.py              # Lógica principal de la aplicación
│   ├── UI Dash           # Componentes de interfaz gráfica
│   ├── Módulo Bayesiano  # Implementaciones de muestreo MCMC
│   └── Generador de PDF  # Sistema de reportes automatizados
├── requirements.txt      # Gestión de dependencias
├── LICENSE               # Licencia MIT
└── docs/                 # Documentación técnica (generada automáticamente)
```

### Diagrama de Flujo de Datos
1. Entrada: Datos crudos (CSV/Excel)
2. Procesamiento: Estimación de parámetros bayesianos
3. Salida:
   - Visualizaciones interactivas (Plotly)
   - Reporte PDF con análisis completo
   - Archivo JSON con metadatos estadísticos

## Glosario Técnico

### Términos Estadísticos
- **Cadena de Markov Monte Carlo (MCMC)**: Algoritmo para muestrear distribuciones complejas
- **Factor de Bayes**: Razón de verosimilitudes para comparación de modelos
- **Intervalo Credible**: Análogo bayesiano al intervalo de confianza

### Componentes de Interfaz
- **Callback Dash**: Mecanismo para actualizar componentes UI reactivamente
- **dcc.Graph**: Contenedor para visualizaciones interactivas de Plotly
- **dbc.Modal**: Ventana emergente para visualización de resultados detallados

## Guías de Implementación

1. Estándares de Código:
   - PEP8 con línea máxima de 100 caracteres
   - Typing hints en todas las funciones
   - Docstrings Google-style

2. Pruebas Automatizadas:
   ```bash
   # Ejecutar suite de pruebas
   pytest --cov=script tests/
   
   # Generar reporte de cobertura
   coverage html
   ```

3. Documentación:
   - Actualizar versión en Sphinx
   - Validar ejemplos de código con doctest


## Licencia
MIT License - ver archivo LICENSE para detalles.