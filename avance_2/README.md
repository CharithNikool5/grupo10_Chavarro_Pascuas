
# Avance 2 — Docker + Jupyter + Machine Learning

## ¿Qué se hizo?

Implementación de Jupyter Notebook en Docker conectado a Supabase

para entrenar un modelo de Regresión Lineal que predice el score

de anime basado en popularidad, favoritos y episodios.

## Tecnologías

- Docker + Docker Compose

- Jupyter Notebook / JupyterLab

- Scikit-learn (LinearRegression)

- Plotly + Matplotlib

## Resultados del Modelo

- R² Entrenamiento : 12.98%

- R² Prueba        : 13.97%

- RMSE             : 0.2253

- Estado           : ✅ Buen ajuste, sin overfitting

## Cómo ejecutar

```bash

cd avance2

docker compose build

docker compose up -d

docker compose logs jupyter  # Obtener token

# Abrir http://localhost:8888

```

