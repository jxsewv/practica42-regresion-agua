---
title: Práctica 4.2 - Regresión Lineal Agua
emoji: 💧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 💧 Práctica 4.2 – Regresión Lineal Múltiple y Correlación

Aplicación web interactiva desarrollada con **Streamlit** y **DuckDB** para la predicción y análisis del **Consumo Per Cápita (CPC)** de agua potable mediante un modelo de regresión lineal múltiple.

---

## 👤 Datos del Estudiante y Contexto Académico

- **Alumno:** José de Jesús Pablo Jiménez
- **Número de Control:** 23680075
- **Materia:** Análisis y Exploración de Datos (INC-2505)
- **Institución:** TecNM Campus Cuautla (Ingeniería en Sistemas Computacionales)
- **Despliegue:** Self-hosted en servidor Linux propio mediante Docker y túnel seguro.

---

## 🛠️ Stack Tecnológico

- **Motor de Datos:** DuckDB (consultas analíticas de alto rendimiento)
- **Procesamiento y Ciencia de Datos:** Python, pandas, NumPy, SciPy, statsmodels, scikit-learn
- **Visualización:** Matplotlib, Seaborn, Plotly Express
- **Interfaz Web:** Streamlit
- **Despliegue y Virtualización:** Docker (Linux Slim base), Cloudflare/Tailscale Tunnel

---

## 📁 Estructura del Proyecto

```text
.
├── .streamlit/
│   └── config.toml          # Configuración de tema visual y servidor Streamlit
├── app.py                   # Código ejecutable de la app web y modelo
├── Dockerfile               # Definición del contenedor Docker (Puerto 7860)
├── requirements.txt         # Dependencias principales (DuckDB, Streamlit, etc.)
├── requirements-extra.txt   # Dependencias secundarias de visualización (Plotly)
└── README.md                # Documentación del proyecto
```

---

## 🚀 Guía Detallada de Instalación y Despliegue

Sigue las instrucciones según el método de despliegue que prefieras. Ambos métodos comienzan con la obtención del código fuente.

### Paso 1: Clonar el Repositorio

Abre tu terminal y clona el proyecto en tu máquina local o servidor:

```bash
git clone https://github.com/jxsewv/practica42-regresion-agua.git
cd practica42-regresion-agua
```

---

### Opción A: Despliegue con Docker (Recomendado)

Ideal para entornos de producción, servidores dedicados o contenedores aislados. El `Dockerfile` configurado levanta la app bajo el puerto **7860** utilizando un usuario sin privilegios de superusuario (`user:1000`).

1. **Asegúrate de tener Docker instalado y ejecutándose:**
   ```bash
   docker --version
   ```

2. **Construir la imagen de Docker:**
   Ejecuta el build en la raíz del proyecto para empaquetar la aplicación y sus dependencias (`requirements.txt` y `requirements-extra.txt`):
   ```bash
   docker build -t regresion-agua:latest .
   ```

3. **Lanzar el contenedor:**
   Inicia el contenedor mapeando el puerto interno `7860` al puerto host `7860` en segundo plano (`-d`):
   ```bash
   docker run -d \
     --name app-regresion-agua \
     -p 7860:7860 \
     --restart unless-stopped \
     regresion-agua:latest
   ```

4. **Verificar el estado del contenedor:**
   ```bash
   docker logs app-regresion-agua
   ```

5. **Acceso a la interfaz:**
   Abre tu navegador web e ingresa a:
   `http://localhost:7860` (o `http://IP-DE-TU-SERVIDOR:7860`).

---

### Opción B: Ejecución Local en Entorno Virtual Python

Ideal para desarrollo, pruebas directas o modificación del código fuente sin usar Docker.

1. **Asegúrate de contar con Python 3.10 o superior:**
   ```bash
   python3 --version
   ```

2. **Crear y activar un entorno virtual (`venv`):**
   - En Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Actualizar gestor de paquetes pip e instalar dependencias:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-extra.txt
   ```

4. **Ejecutar la aplicación Streamlit:**
   Lanza la aplicación indicando explícitamente el puerto del proyecto:
   ```bash
   streamlit run app.py --server.port 7860
   ```

5. **Acceso a la interfaz:**
   Abre tu navegador e ingresa a `http://localhost:7860`.

---

## ⚙️ Arquitectura de Despliegue Self-Hosted y Túnel Seguro

Para exponer esta aplicación a Internet en un servidor propio sin exponer la red local ni abrir puertos en el router:

1. **Exposición del Servicio:** El contenedor Docker corre aislado exponiendo únicamente el puerto `7860`.
2. **Túnel Cifrado:** Se configura un túnel seguro (Cloudflare Tunnel / Tailscale Funnel) apuntando al puerto `7860`.
3. **Publicación Cifrada:** El tráfico externo ingresa vía HTTPS cifrado desde el dominio/subdominio público configurado hacia el servicio local.

---

## 📜 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE) para obtener más detalles sobre el uso, modificación y distribución del código.
