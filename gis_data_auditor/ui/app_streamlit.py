"""
Interfaz Gráfica de Usuario en Streamlit para GIS Data Auditor.
Permite ejecutar auditorías, visualizar métricas y descargar el reporte Excel.
"""

import os
from pathlib import Path
import tempfile
import pandas as pd
import streamlit as st

from gis_data_auditor.config.settings import DEFAULT_OUTPUT_DIR
from gis_data_auditor.core.audit_engine import AuditEngine
from gis_data_auditor.models.validation import Severity
from gis_data_auditor.reports.excel_report_generator import ExcelReportGenerator


def main():
    st.set_page_config(
        page_title="GIS Data Auditor",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🗺️ GIS Data Auditor")
    st.markdown("**Sistema Modular de Auditoría Estructural de Shapefiles mediante Python**")

    # Panel lateral de configuración
    st.sidebar.header("⚙️ Configuración de Entrada")

    # 1. Selección del Excel Estándar
    excel_file = st.sidebar.file_uploader("1. Archivo Excel con Estándar (.xlsx)", type=["xlsx"])
    excel_path_input = st.sidebar.text_input("...o ingrese la ruta local al Excel:", value="c:\\AUTOMATIZACION-PAS\\Diccionario_PAS151.xlsx")

    # 2. Selección de la Carpeta Raíz
    target_folder_input = st.sidebar.text_input("2. Ruta de Carpeta Raíz con Shapefiles:", value="c:\\AUTOMATIZACION-PAS")

    # 3. Ubicación del Reporte de Salida (A Elección del Usuario)
    st.sidebar.subheader("📄 Reporte de Salida")
    output_dir_input = st.sidebar.text_input("Carpeta para guardar el reporte:", value=str(DEFAULT_OUTPUT_DIR.resolve()))
    output_filename_input = st.sidebar.text_input("Nombre del archivo Excel:", value="Reporte_Auditoria_GIS.xlsx")

    # Botón principal
    start_audit = st.sidebar.button("🚀 Iniciar Auditoría", type="primary", use_container_width=True)

    if start_audit:
        # Resolver ruta del Excel
        temp_excel = None
        if excel_file is not None:
            temp_dir = tempfile.mkdtemp()
            temp_excel = os.path.join(temp_dir, excel_file.name)
            with open(temp_excel, "wb") as f:
                f.write(excel_file.getbuffer())
            final_excel_path = temp_excel
        elif excel_path_input and os.path.exists(excel_path_input):
            final_excel_path = excel_path_input
        else:
            st.error("❌ Por favor especifique un archivo Excel válido.")
            return

        # Resolver ruta de la carpeta
        if not target_folder_input or not os.path.exists(target_folder_input):
            st.error(f"❌ La carpeta especificada no existe: '{target_folder_input}'")
            return

        # Ejecutar proceso
        st.info("🔍 Ejecutando auditoría en la carpeta seleccionada...")
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def update_progress(current, total, msg):
            pct = float(current) / float(total) if total > 0 else 1.0
            progress_bar.progress(pct)
            status_text.text(f"Auditando [{current}/{total}]: {msg}")

        engine = AuditEngine(force_fiona=True)
        try:
            report = engine.run_audit(
                excel_path=final_excel_path,
                target_dir=target_folder_input,
                progress_callback=update_progress
            )
            progress_bar.progress(1.0)
            status_text.text("✅ Auditoría completada.")

            # Generar Excel
            out_path = Path(output_dir_input) / output_filename_input
            generator = ExcelReportGenerator()
            final_excel_file = generator.generate_report(report, out_path)

            st.success(f"🎉 Reporte generado exitosamente en: `{final_excel_file}`")

            # Guardar en estado de sesión para visualización
            st.session_state["report"] = report
            st.session_state["excel_path"] = final_excel_file

        except Exception as e:
            st.error(f"❌ Error durante la auditoría: {e}")
            return

    # Visualización de Resultados en Dashboard
    if "report" in st.session_state:
        report = st.session_state["report"]

        st.markdown("---")
        st.subheader("📊 Resumen Ejecutivo")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("SHPs Encontrados", report.total_shps_found)
        col2.metric("SHPs Auditados", report.total_shps_audited)
        col3.metric("Archivos Conformes", report.total_clean_files, delta="Conforme", delta_color="normal")
        col4.metric("Con Errores", report.total_files_with_errors, delta="-Errores" if report.total_files_with_errors > 0 else "0", delta_color="inverse")
        col5.metric("Con Advertencias", report.total_files_with_warnings, delta="-Adv" if report.total_files_with_warnings > 0 else "0", delta_color="off")

        # Botón de Descarga Directa
        if "excel_path" in st.session_state and os.path.exists(st.session_state["excel_path"]):
            with open(st.session_state["excel_path"], "rb") as f:
                st.download_button(
                    label="📥 Descargar Reporte Excel Completo (.xlsx)",
                    data=f,
                    file_name=Path(st.session_state["excel_path"]).name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        # Tabs de detalle
        tab_incidencias, tab_datasets = st.tabs(["⚠️ Detalle de Incidencias", "📁 Estado por Dataset"])

        with tab_incidencias:
            if not report.issues:
                st.balloons()
                st.success("¡No se encontraron incidencias! Todos los Shapefiles cumplen con el estándar.")
            else:
                issues_data = []
                for iss in report.issues:
                    issues_data.append({
                        "Archivo": iss.dataset_name,
                        "Esquema": iss.schema_id,
                        "Campo": iss.field_name,
                        "Severidad": iss.severity.value,
                        "Categoría": iss.category.value,
                        "Esperado": str(iss.expected_value),
                        "Encontrado": str(iss.found_value),
                        "Descripción": iss.message,
                        "Recomendación": iss.recommendation
                    })
                df_issues = pd.DataFrame(issues_data)
                
                # Filtros
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    filter_sev = st.multiselect("Filtrar por Severidad:", options=df_issues["Severidad"].unique(), default=df_issues["Severidad"].unique())
                with col_f2:
                    filter_cat = st.multiselect("Filtrar por Categoría:", options=df_issues["Categoría"].unique(), default=df_issues["Categoría"].unique())

                df_filtered = df_issues[
                    (df_issues["Severidad"].isin(filter_sev)) &
                    (df_issues["Categoría"].isin(filter_cat))
                ]

                st.dataframe(df_filtered, use_container_width=True)

        with tab_datasets:
            datasets_data = []
            for ds in report.datasets:
                datasets_data.append({
                    "SHP": ds.name,
                    "Esquema": ds.associated_schema or "SIN_ESQUEMA",
                    "Estado Asociación": ds.match_status,
                    "Geometría": ds.geometry_type,
                    "CRS": ds.crs_name,
                    "Registros": ds.feature_count,
                    "Total Campos": len(ds.fields),
                    "Ruta": str(ds.filepath)
                })
            df_ds = pd.DataFrame(datasets_data)
            st.dataframe(df_ds, use_container_width=True)


if __name__ == "__main__":
    main()
