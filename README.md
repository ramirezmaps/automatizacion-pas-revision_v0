# GIS Data Auditor

Sistema modular de auditoría de estructuras de datos geoespaciales mediante Python y ArcPy / Fiona.

## 📌 Descripción del Proyecto

**GIS Data Auditor** es una aplicación en Python diseñada para revisar automáticamente la estructura de archivos Shapefile (`.shp`) almacenados en carpetas y subcarpetas, comparándolos contra un estándar definido en Excel.

Permite dos modos de uso:
1. **Modo Independiente (Standalone)**: Interfaz gráfica web local desarrollada en Streamlit, ejecutable sin necesidad de ArcGIS Pro instalada.
2. **Modo Integrado en ArcGIS Pro**: Caja de herramientas nativa de Python (`.pyt`) para ser ejecutada directamente en el panel de Geoprocesamiento de ArcGIS Pro.

---

## 🛠️ Requisitos e Instalación

* **Python**: 3.9 o superior.
* **Librerías principales**: `streamlit`, `fiona`, `geopandas`, `pandas`, `openpyxl`, `pydantic`.

---

## 🚀 Cómo Ejecutar

### Modo Independiente (Interfaz Web)
Haz **doble clic** sobre el ejecutable `Iniciar_Auditor.bat` en la raíz del proyecto o ejecuta:

```bash
streamlit run gis_data_auditor/ui/app_streamlit.py
```

### Modo ArcGIS Pro
1. Abre ArcGIS Pro.
2. En el panel **Catalog**, agrega la toolbox `GIS Data Auditor.pyt`.
3. Abre y ejecuta la herramienta **Auditar Estructura de Shapefiles**.

---

## 📄 Estructura del Reporte Excel Generado

El reporte de salida contiene 5 hojas:
1. **Resumen**: Estadísticas globales y conteo de incidencias por severidad.
2. **Datasets**: Estado de asociación, lectura y conteo de cada Shapefile.
3. **Detalle_Campos**: Inspección campo por campo contra el estándar.
4. **Incidencias**: Catálogo detallado de errores y advertencias con recomendación de corrección.
5. **Estandar_Utilizado**: Copia en memoria del estándar procesado.
