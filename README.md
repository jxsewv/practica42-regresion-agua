title: Práctica 4.2 - Regresión Lineal Agua
emoji: 💧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false

💧 Práctica 4.2 – Regresión Lineal Múltiple y Correlación

Aplicación web interactiva desarrollada con Streamlit y DuckDB para la predicción y análisis del Consumo Per Cápita (CPC) de agua potable mediante un modelo de regresión lineal múltiple.

👤 Datos del Estudiante y Contexto Académico

Alumno: José de Jesús Pablo Jiménez

Número de Control: 23680075

Materia: Análisis y Exploración de Datos (INC-2505)

Institución: TecNM Campus Cuautla (Ingeniería en Sistemas Computacionales)

Despliegue: Self-hosted en servidor Linux propio mediante Docker y túnel seguro.

🛠️ Stack Tecnológico

Motor de Datos: DuckDB (consultas analíticas de alto rendimiento)

Procesamiento y Ciencia de Datos: Python, pandas, NumPy, SciPy, statsmodels, scikit-learn

Visualización: Matplotlib, Seaborn, Plotly Express

Interfaz Web: Streamlit

Despliegue y Virtualización: Docker (Linux Alpine/Slim base), Cloudflare/Tailscale Tunnel

📁 Estructura del Proyecto

.
├── .streamlit/
│   └── config.toml          # Configuración de tema visual y servidor Streamlit
├── app.py                   # Código ejecutable de la app web y modelo
├── Dockerfile               # Definición del contenedor Docker (Puerto 7860)
├── requirements.txt         # Dependencias principales (DuckDB, Streamlit, etc.)
├── requirements-extra.txt   # Dependencias secundarias de visualización (Plotly)
└── README.md                # Documentación del proyecto


🚀 Despliegue e Instalación

Opción A: Contenedor Docker (Recomendado)

El proyecto incluye un Dockerfile optimizado para ejecutarse en el puerto 7860 bajo un usuario sin privilegios root (user:1000).

Construir la imagen Docker:

docker build -t regresion-agua:latest .


Ejecutar el contenedor:

docker run -d -p 7860:7860 --name app-regresion-agua regresion-agua:latest


Acceder a la aplicación:
Abre en tu navegador http://localhost:7860.

Opción B: Ejecución Local en Entorno Virtual

Si deseas probar o modificar el código directamente en tu sistema:

Clonar el repositorio:

git clone https://github.com/TU-USUARIO/practica42-regresion-agua.git
cd practica42-regresion-agua


Crear y activar entorno virtual:

python3 -m venv venv
source venv/bin/activate


Instalar dependencias:

pip install --upgrade pip
pip install -r requirements.txt -r requirements-extra.txt


Ejecutar la aplicación Streamlit:

streamlit run app.py --server.port 7860


⚙️ Arquitectura de Despliegue en Servidor Propio

La aplicación está diseñada para ser self-hosted:

El contenedor Docker expone el servicio en el puerto interno 7860.

Se expone a Internet de forma segura mediante un túnel cifrado (Cloudflare Tunnel / Tailscale) sin necesidad de abrir puertos directamente en el módem/router.
