import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client

# =====================================================================
# CONFIGURACIÓN DE CREDENCIALES (API BACKEND)
# =====================================================================
SUPABASE_URL = "https://ekshvlurmmjerwtukbqb.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_YxRlPMttZ6T-OWBcfYIkcA_-G1J_nUU"

class AppAlumnos:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Alumnos - Supabase CRUD")
        self.root.geometry("460x340")
        self.root.resizable(False, False)
        
        # Centralizar la ventana en la pantalla del usuario
        self.root.eval('tk::PlaceWindow . center')
        
        # Inicializar Cliente de Conexión Segura
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo inicializar el cliente: {e}")

        # Configurar Estilos Modernos y Paleta de Colores
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configurar colores de interfaz limpia (Sistema formal)
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("Accent.TButton", background="#007ACC", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#005999")])
        
        # Variables reactivas para el mapeo de inputs
        self.var_dni = tk.StringVar()
        self.var_apellido_pat = tk.StringVar()
        self.var_apellido_mat = tk.StringVar()
        
        self.inicializar_componentes()

    def inicializar_componentes(self):
        # Contenedor raíz con márgenes de diseño (Padding)
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezado principal del formulario
        lbl_titulo = ttk.Label(main_frame, text="ACTUALIZAR REGISTROS (CRUD)", font=("Segoe UI", 14, "bold"), foreground="#333333")
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # --- ESTRUCTURA DE CAMPOS ---
        # Componente: DNI (Llave primaria de búsqueda / Cláusula WHERE)
        ttk.Label(main_frame, text="DNI del Alumno *:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        txt_dni = ttk.Entry(main_frame, textvariable=self.var_dni, font=("Segoe UI", 10), width=26)
        txt_dni.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        txt_dni.focus() # Auto-focus en el campo primario al abrir

        # Componente: Apellido Paterno (Cláusula SET)
        ttk.Label(main_frame, text="Nuevo Apellido Pat:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
        ttk.Entry(main_frame, textvariable=self.var_apellido_pat, font=("Segoe UI", 10), width=26).grid(row=2, column=1, padx=5, pady=8, sticky="w")

        # Componente: Apellido Materno (Cláusula SET)
        ttk.Label(main_frame, text="Nuevo Apellido Mat:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
        ttk.Entry(main_frame, textvariable=self.var_apellido_mat, font=("Segoe UI", 10), width=26).grid(row=3, column=1, padx=5, pady=8, sticky="w")

        # Línea divisoria formal
        ttk.Separator(main_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=15)

        # Sub-contenedor para botones de acción (Alineación derecha)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="e")

        # Botón secundario: Limpieza del Formulario
        btn_limpiar = ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario)
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Botón primario: Transacción de Base de Datos
        btn_actualizar = ttk.Button(btn_frame, text="Actualizar en DB", style="Accent.TButton", command=self.procesar_crud_update)
        btn_actualizar.pack(side=tk.LEFT, padx=5)

    def limpiar_formulario(self):
        self.var_dni.set("")
        self.var_apellido_pat.set("")
        self.var_apellido_mat.set("")

    def procesar_crud_update(self):
        # Sanitizar entradas limpiando espacios en blanco accidentales
        dni = self.var_dni.get().strip()
        apellido_pat = self.var_apellido_pat.get().strip()
        apellido_mat = self.var_apellido_mat.get().strip()

        # Regla de negocio básica: Validar parámetro de búsqueda indispensable
        if not dni:
            messagebox.showwarning("Dato requerido", "El DNI es obligatorio para identificar al alumno.")
            return

        # Construcción dinámica del payload JSON para la API rest
        payload_update = {}
        if apellido_pat: payload_update["APELLIDO_PAT"] = apellido_pat
        if apellido_mat: payload_update["APELLIDO_MAT"] = apellido_mat

        if not payload_update:
            messagebox.showwarning("Campos ausentes", "Debe ingresar al menos un apellido nuevo para procesar la actualización.")
            return

        # Ejecución de la consulta asíncrona hacia Supabase
        try:
            response = self.supabase.from_("ALUMNOS").update(payload_update).eq("DNI", dni).execute()

            # Analizar el conjunto de datos retornado por la base de datos
            if len(response.data) == 0:
                messagebox.showwarning("Operación fallida", f"No se encontró ningún registro que coincida con el DNI: {dni}")
            else:
                registro = response.data[0]
                mensaje_exito = (
                    f"Transacción exitosa en el backend.\n\n"
                    f"🔹 ID asignado: {registro.get('id')}\n"
                    f"🔹 DNI consultado: {registro.get('DNI')}\n"
                    f"🔹 Apellido Paterno: {registro.get('APELLIDO_PAT')}\n"
                    f"🔹 Apellido Materno: {registro.get('APELLIDO_MAT')}\n"
                    f"🔹 Registro modificado el: {registro.get('created_at')}"
                )
                messagebox.showinfo("CRUD Update OK", mensaje_exito)
                self.limpiar_formulario()

        except Exception as error_db:
            messagebox.showerror("Error crítico de red/DB", f"La transacción fue rechazada por el servidor:\n{error_db}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppAlumnos(root)
    root.mainloop()
