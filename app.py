import streamlit as st
from supabase import create_client, Client

# =====================================================================
# CONFIGURACIÓN DE CREDENCIALES (API BACKEND)
# =====================================================================
# Streamlit intentará leer las claves seguras desde los Secrets que configuraste.
# Si no las encuentra ahí, usará las que pusiste por defecto abajo.
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_ANON_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://ekshvlurmmjerwtukbqb.supabase.co"
    SUPABASE_ANON_KEY = "sb_publishable_YxRlPMttZ6T-OWBcfYIkcA_-G1J_nUU"

# Inicializar Cliente de Conexión Segura
@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        st.error(f"No se pudo inicializar el cliente de Supabase: {e}")
        return None

supabase: Client = init_supabase()

# =====================================================================
# INTERFAZ GRÁFICA CON STREAMLIT (Sustituye a Tkinter)
# =====================================================================
st.title("Gestor de Alumnos - Supabase CRUD")
st.subheader("ACTUALIZAR REGISTROS (CRUD)")

# --- ESTRUCTURA DE CAMPOS DE ENTRADA ---
dni = st.text_input("DNI del Alumno *:", max_chars=15).strip()
apellido_pat = st.text_input("Nuevo Apellido Paterno:").strip()
apellido_mat = st.text_input("Nuevo Apellido Materno:").strip()

st.markdown("---")

# Sub-contenedor para botones de acción (Alineación horizontal)
col1, col2 = st.columns([1, 5])

with col1:
    # Botón para simular limpieza (En Streamlit las páginas se recargan solas)
    btn_limpiar = st.button("Limpiar")
    if btn_limpiar:
        st.rerun()

with col2:
    # Botón primario: Transacción de Base de Datos
    btn_actualizar = st.button("Actualizar en DB", type="primary")

# --- PROCESAR ACCIÓN DE ACTUALIZACIÓN ---
if btn_actualizar:
    # Regla de negocio básica: Validar parámetro de búsqueda indispensable
    if not dni:
        st.warning("⚠️ El DNI es obligatorio para identificar al alumno.")
    else:
        # Construcción dinámica del payload para la base de datos
        payload_update = {}
        if apellido_pat: 
            payload_update["APELLIDO_PAT"] = apellido_pat
        if apellido_mat: 
            payload_update["APELLIDO_MAT"] = apellido_mat

        if not payload_update:
            st.warning("⚠️ Debe ingresar al menos un apellido nuevo para procesar la actualización.")
        else:
            # Ejecución de la consulta hacia Supabase
            try:
                if supabase:
                    response = supabase.from_("ALUMNOS").update(payload_update).eq("DNI", dni).execute()

                    # Analizar el conjunto de datos retornado por la base de datos
                    if len(response.data) == 0:
                        st.error(f"❌ No se encontró ningún registro que coincida con el DNI: {dni}")
                    else:
                        registro = response.data[0]
                        
                        # Mensaje formal de éxito en pantalla
                        st.success("🎉 ¡Transacción exitosa en el backend!")
                        
                        # Mostrar el registro modificado de forma ordenada
                        st.markdown(f"""
                        **Datos actualizados:**
                        * 🔹 **ID asignado:** {registro.get('id')}
                        * 🔹 **DNI consultado:** {registro.get('DNI')}
                        * 🔹 **Apellido Paterno:** {registro.get('APELLIDO_PAT')}
                        * 🔹 **Apellido Materno:** {registro.get('APELLIDO_MAT')}
                        * 🔹 **Registro modificado el:** {registro.get('created_at')}
                        """)
                else:
                    st.error("Error: El cliente de Supabase no está conectado.")
                    
            except Exception as error_db:
                st.error(f"💥 La transacción fue rechazada por el servidor:\n\n{error_db}")
