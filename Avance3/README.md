# Avance 3 — Modelos de Clasificación y Regresión Avanzada

## ¿Qué se hizo?
Evolución del proyecto mediante la implementación de modelos de aprendizaje supervisado más complejos. Se pasó de una Regresión Lineal simple a modelos basados en árboles (CART) y clasificación logística para profundizar en la relación entre los atributos del anime y su éxito.

## Modelos Implementados
1. **Árbol de Decisión (Clasificación)**: Predicción de categorías de éxito.
2. **Árbol de Decisión (Regresión)**: Modelado no lineal del score.
3. **Regresión Logística**: Clasificación binaria con probabilidades calibradas.

## Tecnologías
* **Entorno**: Docker + Jupyter Server (vía venv en este avance).
* **Modelado**: Scikit-learn (DecisionTreeClassifier, DecisionTreeRegressor, LogisticRegression).
* **Métricas**: F1-Score, Curva ROC/AUC, R² y RMSE.
* **Visualización**: Seaborn, Matplotlib y visualización de estructuras de árboles (plot_tree).

## Resultados Destacados
* **Estabilidad**: Los modelos de Árboles muestran una variación menor al 5% entre splits, indicando un buen nivel de generalización.
* **Hallazgo clave**: Se identificó que el árbol CART captura mejor las no-linealidades de los datos en comparación con los modelos lineales previos.
* **Optimización**: Se recomienda el uso de `max_depth` y `min_samples_leaf` para evitar el sobreajuste (overfitting) detectado en los árboles más profundos.

## Cómo ejecutar
```bash
# Acceder a la carpeta del avance
cd avance3

# Activar el entorno virtual
source venv/bin/activate

# Iniciar Jupyter (usar el puerto configurado y permitir root si es necesario)
jupyter notebook --no-browser --port=8888 --allow-root

# Abrir los notebooks en:
# notebooks/ArbolDecisionClasificacion.ipynb
# notebooks/ArbolDecisionRegresion.ipynb
# notebooks/RegresionLogistica.ipynb
