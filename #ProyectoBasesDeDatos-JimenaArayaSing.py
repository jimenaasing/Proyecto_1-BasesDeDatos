#ProyectoBasesDeDatos-JimenaArayaSing
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import customtkinter as ctk
import psycopg2

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppAgenda(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agenda 3 Patitos")
        self.geometry("1280x760")
        self.minsize(1050, 650)

        self.conn_params = {
            "dbname": "agenda",
            "user": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": "5432",
        }

        self.usuarios_combo = {}
        self.categorias_combo = {}
        self.categorias_padre_combo = {}
        self.ubicaciones_combo = {} #Agregado por Jimena por el RF-08
        self.disponibilidades_combo = {} #Agregado por Jimena por el RF-11 y RF-12
        self.tipos_disponibilidad_combo = {} #Agregado por Jimena por el RF-11 y RF-12
        self.eventos_combo = {} #Agregado por Jimena por el modulo Tareas Asociadas a Eventos 

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.crear_sidebar()
        self.crear_area_principal()
        self.configurar_estilos()

        self.actualizar_todas_las_tablas()

        if DateEntry is None:
            self.after(500, lambda: messagebox.showwarning(
                "Calendario no instalado",
                "Para usar los selectores de fecha instala:\n\npip install tkcalendar"
            ))

    # -------------------- INFRAESTRUCTURA --------------------

    def obtener_conexion(self):
        conn = psycopg2.connect(**self.conn_params)
        with conn.cursor() as cur:
            cur.execute("SET search_path TO prototipo, public;")
        return conn

    def ejecutar_consulta(self, sql, params=None, fetch=False):
        conn = None
        try:
            conn = self.obtener_conexion()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() if fetch else None
            conn.commit()
            return rows
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def crear_treeview(self, parent, columnas, widths):
        contenedor = ctk.CTkFrame(parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        tree = ttk.Treeview(contenedor, columns=columnas, show="headings")
        for col, width in zip(columnas, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        return tree

    def seleccionar_modulo(self, nombre):
        self.tabview.set(nombre)
        for modulo, boton in self.botones_nav.items():
            boton.configure(fg_color=("gray75", "gray25") if modulo == nombre else "transparent")

    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=235, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(
            self.sidebar_frame,
            text="📅 AGENDA 🦆🦆🦆",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(28, 5), sticky="w")

        ctk.CTkLabel(
            self.sidebar_frame,
            text="Gestión de usuarios, categorías y eventos",
            font=ctk.CTkFont(size=11),
            wraplength=190,
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        self.botones_nav = {}
        for i, (nombre, icono) in enumerate([
            ("Usuarios", "👥"),
            ("Categorías", "📁"),
            ("Eventos", "🗓️"),
            ("Ubicaciones", "🏢"), #Agregado por Jimena por el RF-08
            ("Disponibilidad", "🕛"), #Agregado por Jimena por el RF-11 y RF-12
            ("Tareas", "✍️"), #Agregado por Jimena por el modulo tareas Asociadas a Eventos 
        ], start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=f"{icono}  {nombre}",
                anchor="w", fg_color="transparent",
                command=lambda n=nombre: self.seleccionar_modulo(n)
            )
            btn.grid(row=i, column=0, padx=15, pady=5, sticky="ew")
            self.botones_nav[nombre] = btn

        ctk.CTkButton(
            self.sidebar_frame,
            text="🔄  Recargar datos",
            command=self.actualizar_todas_las_tablas
        ).grid(row=8, column=0, padx=15, pady=(20, 5), sticky="ew")

        ctk.CTkLabel(self.sidebar_frame, text="APARIENCIA", font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=11, column=0, padx=20, pady=(10, 5), sticky="w"
        )
        self.option_mode = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["System", "Dark", "Light"],
            command=ctk.set_appearance_mode
        )
        self.option_mode.set("System")
        self.option_mode.grid(row=12, column=0, padx=15, pady=(0, 25), sticky="ew")

    def crear_area_principal(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.main_container, command=self.al_cambiar_pestana)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_usuarios = self.tabview.add("Usuarios")
        self.tab_categorias = self.tabview.add("Categorías")
        self.tab_eventos = self.tabview.add("Eventos")
        self.tab_ubicaciones = self.tabview.add("Ubicaciones") #Agregado por Jimena por el RF-08
        self.tab_disponibilidad = self.tabview.add("Disponibilidad") #Agregado por Jimena por el RF-11 y RF-12
        self.tab_tareas = self.tabview.add("Tareas") #Agregado por Jimena por el modulo de Tareas Asociadas a Eventos 

        self.configurar_pestana_usuarios()
        self.configurar_pestana_categorias()
        self.configurar_pestana_eventos()
        self.configurar_pestana_ubicaciones()  #Agregado por Jimena por el RF-08
        self.configurar_pestana_disponibilidad() #Agregado por Jimena por el RF-11 y RF-12
        self.seleccionar_modulo("Usuarios")
        self.configurar_pestana_tareas() #Agregado por Jimena por el modulo de Tareas Asociadas a Eventos 

    def al_cambiar_pestana(self):
        nombre = self.tabview.get()
        if nombre in self.botones_nav:
            for modulo, boton in self.botones_nav.items():
                boton.configure(fg_color=("gray75", "gray25") if modulo == nombre else "transparent")

    def crear_encabezado(self, parent, titulo, descripcion):
        ctk.CTkLabel(parent, text=titulo, font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        ctk.CTkLabel(parent, text=descripcion, font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=15, pady=(0, 12)
        )

    # -------------------- USUARIOS --------------------

    def configurar_pestana_usuarios(self):
        self.crear_encabezado(self.tab_usuarios, "Usuarios", "Registra, consulta y administra los usuarios de la agenda.")

        cuerpo = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla_frame = ctk.CTkFrame(cuerpo)
        tabla_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=300)
        form.grid(row=0, column=1, sticky="nsew")

        self.tree_usuarios = self.crear_treeview(
            tabla_frame, ("ID", "Nombre", "Apellido", "Registro", "Activo"),
            (70, 160, 160, 160, 80)
        )
        self.tree_usuarios.bind("<<TreeviewSelect>>", self.cargar_usuario_seleccionado)

        ctk.CTkLabel(form, text="Formulario de usuario", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_nombre = ctk.CTkEntry(form, placeholder_text="Nombre")
        self.entry_nombre.pack(fill="x", padx=10, pady=6)
        self.entry_apellido = ctk.CTkEntry(form, placeholder_text="Apellido")
        self.entry_apellido.pack(fill="x", padx=10, pady=6)

        self.switch_usuario_activo = ctk.CTkSwitch(form, text="Usuario activo")
        self.switch_usuario_activo.select()
        self.switch_usuario_activo.pack(anchor="w", padx=12, pady=10)

        ctk.CTkButton(form, text="➕ Registrar usuario", command=self.agregar_usuario).pack(fill="x", padx=10, pady=(12, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionado", command=self.actualizar_usuario).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nuevo / Limpiar", command=self.limpiar_form_usuario, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionado", command=self.eliminar_usuario, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)


    def usuario_seleccionado_id(self):
        sel = self.tree_usuarios.selection()
        return self.tree_usuarios.item(sel[0])["values"][0] if sel else None

    def cargar_usuario_seleccionado(self, _=None):
        sel = self.tree_usuarios.selection()
        if not sel:
            return
        vals = self.tree_usuarios.item(sel[0])["values"]
        self.entry_nombre.delete(0, tk.END); self.entry_nombre.insert(0, vals[1])
        self.entry_apellido.delete(0, tk.END); self.entry_apellido.insert(0, vals[2])
        if vals[4]:
            self.switch_usuario_activo.select()
        else:
            self.switch_usuario_activo.deselect()

    def limpiar_form_usuario(self):
        self.tree_usuarios.selection_remove(self.tree_usuarios.selection())
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.switch_usuario_activo.select()

    def agregar_usuario(self):
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning("Campos incompletos", "Indica nombre y apellido.")
        try:
            self.ejecutar_consulta("INSERT INTO usuarios (nombre, apellido, activo) VALUES (%s, %s, %s)",
                                   (nombre, apellido, self.switch_usuario_activo.get() == 1))
            self.limpiar_form_usuario(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))

    def actualizar_usuario(self):
        uid = self.usuario_seleccionado_id()
        if uid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona un usuario para actualizar.")
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning("Campos incompletos", "Indica nombre y apellido.")
        try:
            self.ejecutar_consulta("UPDATE usuarios SET nombre=%s, apellido=%s, activo=%s WHERE id_usuario=%s",
                                   (nombre, apellido, self.switch_usuario_activo.get() == 1, uid))
            self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Usuario actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_usuario(self):
        uid = self.usuario_seleccionado_id()
        if uid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona un usuario.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario seleccionado?"):
            return
        try:
            self.ejecutar_consulta("DELETE FROM usuarios WHERE id_usuario=%s", (uid,))
            self.limpiar_form_usuario(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Eliminado", "Usuario eliminado.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_usuarios(self):
        try:
            rows = self.ejecutar_consulta(
                "SELECT id_usuario, nombre, apellido, fecha_registro, activo FROM usuarios ORDER BY nombre, apellido",
                fetch=True
            )
            for item in self.tree_usuarios.get_children(): self.tree_usuarios.delete(item)
            self.usuarios_combo = {}
            for row in rows:
                registro = row[3].strftime("%Y-%m-%d %H:%M") if hasattr(row[3], "strftime") else row[3]
                self.tree_usuarios.insert("", "end", values=(row[0], row[1], row[2], registro, "Sí" if row[4] else "No"))
                etiqueta = f"{row[1]} {row[2]} — #{row[0]}"
                self.usuarios_combo[etiqueta] = row[0]
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    # -------------------- CATEGORÍAS --------------------

    def configurar_pestana_categorias(self):
        self.crear_encabezado(self.tab_categorias, "Categorías", "Organiza los eventos mediante categorías y subcategorías.")

        cuerpo = ctk.CTkFrame(self.tab_categorias, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320); form.grid(row=0, column=1, sticky="nsew")

        self.tree_categorias = self.crear_treeview(tabla, ("ID", "Categoría", "Categoría padre"), (80, 230, 230))
        self.tree_categorias.bind("<<TreeviewSelect>>", self.cargar_categoria_seleccionada)

        ctk.CTkLabel(form, text="Formulario de categoría", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_cat_nombre = ctk.CTkEntry(form, placeholder_text="Nombre de la categoría")
        self.entry_cat_nombre.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Categoría padre").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_cat_padre = ctk.CTkComboBox(form, values=["Sin categoría padre"], state="readonly")
        self.combo_cat_padre.set("Sin categoría padre")
        self.combo_cat_padre.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(form, text="➕ Crear categoría", command=self.agregar_categoria).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionada", command=self.actualizar_categoria).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nueva / Limpiar", command=self.limpiar_form_categoria, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionada", command=self.eliminar_categoria, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

    def categoria_seleccionada_id(self):
        sel = self.tree_categorias.selection()
        return self.tree_categorias.item(sel[0])["values"][0] if sel else None

    def cargar_categoria_seleccionada(self, _=None):
        sel = self.tree_categorias.selection()
        if not sel: return
        vals = self.tree_categorias.item(sel[0])["values"]
        self.entry_cat_nombre.delete(0, tk.END); self.entry_cat_nombre.insert(0, vals[1])
        padre = vals[2]
        self.combo_cat_padre.set(padre if padre in self.categorias_padre_combo else "Sin categoría padre")

    def limpiar_form_categoria(self):
        self.tree_categorias.selection_remove(self.tree_categorias.selection())
        self.entry_cat_nombre.delete(0, tk.END); self.combo_cat_padre.set("Sin categoría padre")

    def _padre_id_actual(self):
        valor = self.combo_cat_padre.get()
        return None if valor == "Sin categoría padre" else self.categorias_padre_combo.get(valor)

    def agregar_categoria(self):
        nombre = self.entry_cat_nombre.get().strip()
        if not nombre: return messagebox.showwarning("Campo requerido", "Indica el nombre de la categoría.")
        try:
            self.ejecutar_consulta("INSERT INTO categorias (nombre, id_categoria_padre) VALUES (%s, %s)",
                                   (nombre, self._padre_id_actual()))
            self.limpiar_form_categoria(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Categoría creada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_categoria(self):
        cid = self.categoria_seleccionada_id()
        if cid is None: return messagebox.showwarning("Selección requerida", "Selecciona una categoría.")
        nombre = self.entry_cat_nombre.get().strip(); padre = self._padre_id_actual()
        if not nombre: return messagebox.showwarning("Campo requerido", "Indica el nombre.")
        if padre == cid: return messagebox.showwarning("Relación inválida", "Una categoría no puede ser su propia categoría padre.")
        try:
            self.ejecutar_consulta("UPDATE categorias SET nombre=%s, id_categoria_padre=%s WHERE id_categoria=%s",
                                   (nombre, padre, cid))
            self.actualizar_todas_las_tablas(); messagebox.showinfo("Éxito", "Categoría actualizada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_categoria(self):
        cid = self.categoria_seleccionada_id()
        if cid is None: return messagebox.showwarning("Selección requerida", "Selecciona una categoría.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar la categoría seleccionada?"): return
        try:
            self.ejecutar_consulta("DELETE FROM categorias WHERE id_categoria=%s", (cid,))
            self.limpiar_form_categoria(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Eliminado", "Categoría eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_categorias(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT c.id_categoria, c.nombre, p.nombre
                FROM categorias c
                LEFT JOIN categorias p ON p.id_categoria = c.id_categoria_padre
                ORDER BY c.nombre
            """, fetch=True)
            ids = self.ejecutar_consulta("SELECT id_categoria, nombre FROM categorias ORDER BY nombre", fetch=True)

            for item in self.tree_categorias.get_children(): self.tree_categorias.delete(item)
            self.categorias_combo = {}
            self.categorias_padre_combo = {}
            for cid, nombre in ids:
                etiqueta = f"{nombre} — #{cid}"
                self.categorias_combo[etiqueta] = cid
                self.categorias_padre_combo[etiqueta] = cid
            for row in rows:
                padre = "Sin categoría padre"
                if row[2] is not None:
                    # Buscar etiqueta completa del padre
                    for etiqueta, cid in self.categorias_padre_combo.items():
                        if etiqueta.startswith(f"{row[2]} —"):
                            padre = etiqueta; break
                self.tree_categorias.insert("", "end", values=(row[0], row[1], padre))

            valores_padre = ["Sin categoría padre"] + list(self.categorias_padre_combo.keys())
            self.combo_cat_padre.configure(values=valores_padre)
            if self.combo_cat_padre.get() not in valores_padre:
                self.combo_cat_padre.set("Sin categoría padre")
        except Exception as e:
            print(f"Error cargando categorías: {e}")

 # -------------------- UBICACIONES (Agregado originalmente por Jimena por el RF-08) 
    def configurar_pestana_ubicaciones (self):
        self.crear_encabezado(self.tab_ubicaciones,"Ubicaciones", "Administra los recintos físicos donde se realizan los eventos.")
        subtabs = ctk.CTkTabview(self.tab_ubicaciones)
        subtabs.pack(fill="both", expand=True, padx=10, pady=5)

        tab_gestion = subtabs.add("Gestión") #Agregado por Jimena para el RF-08
        tab_historial = subtabs.add("Histórico") #Agregado por Jimena para el RF-09
        tab_ranking = subtabs.add("Ranking") #Agregado por Jimena para el RF-10

##Agregado por Jimena para el RF-8 
        cuerpo = ctk.CTkFrame(tab_gestion, fg_color="transparent") #Corregido mientras realizaba RF-10
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320); form.grid(row=0, column=1, sticky="nsew")

        self.tree_ubicaciones = self.crear_treeview(
        tabla, ("ID", "Nombre", "Ciudad", "Dirección", "Capacidad"), #Cambio por problema cuando agregue el historico de ubicacion (RF-09 )
        (60, 150, 200, 120, 90))

        self.tree_ubicaciones.bind("<<TreeviewSelect>>", self.cargar_ubicacion_seleccionada)

        ctk.CTkLabel(form, text="Formulario de ubicación", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_ubi_nombre = ctk.CTkEntry(form, placeholder_text="Nombre del recinto")
        self.entry_ubi_nombre.pack(fill="x", padx=10, pady=6)
        self.entry_ubi_direccion = ctk.CTkEntry(form, placeholder_text="Dirección")
        self.entry_ubi_direccion.pack(fill="x", padx=10, pady=6)
        self.entry_ubi_ciudad = ctk.CTkEntry(form, placeholder_text="Ciudad")
        self.entry_ubi_ciudad.pack(fill="x", padx=10, pady=6)
        self.entry_ubi_capacidad = ctk.CTkEntry(form, placeholder_text="Capacidad")
        self.entry_ubi_capacidad.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(form, text="Registrar ubicación", command=self.agregar_ubicacion).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="Actualizar seleccionada", command=self.actualizar_ubicacion).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Nueva / Limpiar", command=self.limpiar_form_ubicacion, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Eliminar ubicacion seleccionada", command=self.eliminar_ubicacion,
                  fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        #Agregado por Jimena por el RF-09 (este es el panel de histórico por ubicación)
        historial_frame = ctk.CTkFrame(tab_historial, fg_color="transparent")  #Corregido mientras realizaba RF-10
        historial_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        ctk.CTkLabel(historial_frame, text="Histórico de eventos por ubicación",
                    font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        fila_selector = ctk.CTkFrame(historial_frame, fg_color="transparent")
        fila_selector.pack(fill="x", padx=10, pady=(0, 8))

        self.combo_historial_ubicacion = ctk.CTkComboBox(
            fila_selector, values=["Seleccione una ubicación"], state="readonly", width=280
        )
        self.combo_historial_ubicacion.set("Seleccione una ubicación")
        self.combo_historial_ubicacion.pack(side="left", padx=(0, 10))

        ctk.CTkButton(fila_selector, text="Consultar el histórico",
                    command=self.cargar_historico_ubicacion).pack(side="left")

        self.tree_historial_ubicacion = self.crear_treeview(
            historial_frame,
            ("ID", "Título", "Categoría", "Propietario", "Inicio", "Fin"),
            (60, 180, 140, 160, 140, 140)
        )


        #Agregado por Jimena por el RF-10 PARA CREAR subpestaña
        ranking_frame = ctk.CTkFrame(tab_ranking, fg_color="transparent")
        ranking_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        fila_titulo_ranking = ctk.CTkFrame(ranking_frame, fg_color="transparent")
        fila_titulo_ranking.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(fila_titulo_ranking, text="Ranking de ocupación de espacios (solo lectura)",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

        ctk.CTkButton(fila_titulo_ranking, text="🔄 Actualizar ranking",
                      command=self.cargar_ranking_ubicaciones, width=160).pack(side="right")

        self.tree_ranking_ubicaciones = self.crear_treeview(
            ranking_frame,
            ("Ubicación", "Ciudad", "Total de eventos"),
            (220, 140, 140)
        )

        
    def ubicacion_seleccionada_id(self):
        sel = self.tree_ubicaciones.selection()
        return self.tree_ubicaciones.item(sel[0])["values"][0] if sel else None

    def cargar_ubicacion_seleccionada(self, _=None):
        sel = self.tree_ubicaciones.selection()
        if not sel:
            return
        vals = self.tree_ubicaciones.item(sel[0])["values"]
        self.entry_ubi_nombre.delete(0, tk.END); self.entry_ubi_nombre.insert(0, vals[1])
        self.entry_ubi_ciudad.delete(0, tk.END); self.entry_ubi_ciudad.insert(0, vals[2]) #Corregido mientras se realizaba el RF-10 por Jimena
        self.entry_ubi_direccion.delete(0, tk.END); self.entry_ubi_direccion.insert(0, vals[3])
        self.entry_ubi_capacidad.delete(0, tk.END); self.entry_ubi_capacidad.insert(0, vals[4])

    def limpiar_form_ubicacion(self):
        self.tree_ubicaciones.selection_remove(self.tree_ubicaciones.selection())
        self.entry_ubi_nombre.delete(0, tk.END)
        self.entry_ubi_direccion.delete(0, tk.END)
        self.entry_ubi_ciudad.delete(0, tk.END)
        self.entry_ubi_capacidad.delete(0, tk.END)

    def _datos_ubicacion_formulario(self):
        nombre = self.entry_ubi_nombre.get().strip()
        direccion = self.entry_ubi_direccion.get().strip()
        ciudad = self.entry_ubi_ciudad.get().strip()
        capacidad = self.entry_ubi_capacidad.get().strip()
        if not nombre or not direccion or not ciudad or not capacidad:
            raise ValueError("Todos los campos son obligatoriosS")
        if not capacidad.isdigit() or int(capacidad) <= 0:
            raise ValueError("La capacidad debe ser un número entero mayor a 0.")
        return nombre, direccion, ciudad, int(capacidad)

    def agregar_ubicacion(self): #Este bloque lo que hace es que guarda una nueva ubicación en la base de datos utilizando los datos de un formulario y actualiza la interfaz gráfica :p
        try:
            datos = self._datos_ubicacion_formulario()
            self.ejecutar_consulta(
                "INSERT INTO ubicaciones (nombre, direccion, ciudad, capacidad) VALUES (%s, %s, %s, %s)",
                datos
            )
            self.limpiar_form_ubicacion(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Ubicación registrada correctamente.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))

    def actualizar_ubicacion(self):
        uid = self.ubicacion_seleccionada_id()
        if uid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona una ubicación para actualizar.")
        try:
            nombre, direccion, ciudad, capacidad = self._datos_ubicacion_formulario()
            self.ejecutar_consulta(
                "UPDATE ubicaciones SET nombre=%s, direccion=%s, ciudad=%s, capacidad=%s WHERE id_ubicacion=%s",
                (nombre, direccion, ciudad, capacidad, uid)
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Ubicación actualizada.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_ubicacion(self):
            uid = self.ubicacion_seleccionada_id()
            if uid is None:
                return messagebox.showwarning("Selección requerida", "Selecciona una ubicación.")
            if not messagebox.askyesno("Confirmar", "¿Eliminar la ubicación seleccionada?"):
                return
            try:
                self.ejecutar_consulta("DELETE FROM ubicaciones WHERE id_ubicacion=%s", (uid,))
                self.limpiar_form_ubicacion(); self.actualizar_todas_las_tablas()
                messagebox.showinfo("Eliminado", "Ubicación eliminada.")
            except psycopg2.errors.ForeignKeyViolation:
                messagebox.showerror(
                    "No se puede eliminar",
                    "Esta ubicación ya tiene eventos asociados.Tiene que eliminar esos eventos primero."
                )
            except Exception as e:
                    messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_ubicaciones(self):
            try:
                rows = self.ejecutar_consulta(
                    "SELECT id_ubicacion, nombre, direccion, ciudad, capacidad FROM ubicaciones ORDER BY nombre",
                    fetch=True
                )
                for item in self.tree_ubicaciones.get_children():
                    self.tree_ubicaciones.delete(item)
                self.ubicaciones_combo = {}
                for row in rows:
                    self.tree_ubicaciones.insert("", "end", values=row)
                    etiqueta = f"{row[1]} — {row[3]} (#{row[0]})"
                    self.ubicaciones_combo[etiqueta] = row[0]

                valores_hist = ["Seleccione una ubicación"] + list(self.ubicaciones_combo.keys())  #Agregado por Jimena por el RF-09 (corregido)
                self.combo_historial_ubicacion.configure(values=valores_hist)

                self.cargar_ranking_ubicaciones()#Agregado por Jimena por el RF-10

            except Exception as e:
                print(f"Error cargando ubicaciones: {e}")



#Agregado por Jimena por el RF-09 (esto lo que hace es carga el historial de eventos de una ubicación específica y los muestra en una tabla )
    def cargar_historico_ubicacion(self):
        etiqueta = self.combo_historial_ubicacion.get()
        id_ubicacion = self.ubicaciones_combo.get(etiqueta)
        if id_ubicacion is None:
            return messagebox.showwarning("Es requerido seleccionar", "Selecciona una ubicación primero.")
        try:                                        #esto ordena cronológicamente los eventos programados para una ubicación 
            rows = self.ejecutar_consulta("""
                SELECT e.id_evento, e.titulo, c.nombre, 
                    u.nombre || ' ' || u.apellido, 
                    e.fecha_inicio, e.fecha_fin
                FROM eventos e
                JOIN categorias c ON c.id_categoria = e.id_categoria
                JOIN usuarios u ON u.id_usuario = e.id_usuario_propietario
                WHERE e.id_ubicacion = %s
                ORDER BY e.fecha_inicio DESC
            """, (id_ubicacion,), fetch=True)

            for item in self.tree_historial_ubicacion.get_children():
                    self.tree_historial_ubicacion.delete(item)

            if not rows:
                    messagebox.showinfo("Sin resultados", "Esta ubicación no tiene eventos registrados.")
                    return
            for row in rows:
                inicio = row[4].strftime("%Y-%m-%d %H:%M") if hasattr(row[4], "strftime") else row[4]
                fin = row[5].strftime("%Y-%m-%d %H:%M") if hasattr(row[5], "strftime") else row[5]
                self.tree_historial_ubicacion.insert("", "end", values=(row[0], row[1], row[2], row[3], inicio, fin))
        except Exception as e:
            messagebox.showerror("Error al consultar", str(e))
    #Agregado por Jimena por el RF-10
    def cargar_ranking_ubicaciones(self):
        try:
            rows = self.ejecutar_consulta(
                "SELECT id_ubicacion, nombre, ciudad, total_eventos FROM vista_ranking_ubicaciones",
                fetch=True
            )
            for item in self.tree_ranking_ubicaciones.get_children():
                self.tree_ranking_ubicaciones.delete(item)
            for row in rows:
                self.tree_ranking_ubicaciones.insert("", "end", values=(row[1], row[2], row[3]))
        except Exception as e:
            print(f"Error cargando ranking de ubicaciones: {e}")


    # -------------------- EVENTOS --------------------

    def configurar_pestana_eventos(self):
        self.crear_encabezado(self.tab_eventos, "Eventos", "Programa eventos seleccionando usuarios, categorías, fechas y horas.")

        cuerpo = ctk.CTkFrame(self.tab_eventos, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=350); form.grid(row=0, column=1, sticky="nsew")

        self.tree_eventos = self.crear_treeview(
            tabla, ("ID", "Propietario", "Categoría","Ubicación", "Título", "Inicio", "Fin"), #Agregado por Jimena por el RF-09 (lo que agregue fue ubicacion)
            (70, 170, 150, 220, 150, 150, 150)
        )
        self.tree_eventos.bind("<<TreeviewSelect>>", self.cargar_evento_seleccionado)

        ctk.CTkLabel(form, text="Formulario de evento", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 12))
        self.entry_ev_titulo = ctk.CTkEntry(form, placeholder_text="Título del evento")
        self.entry_ev_titulo.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Propietario").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_ev_usuario = ctk.CTkComboBox(form, values=["Seleccione un usuario"], state="readonly")
        self.combo_ev_usuario.set("Seleccione un usuario")
        self.combo_ev_usuario.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Categoría").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_ev_categoria = ctk.CTkComboBox(form, values=["Seleccione una categoría"], state="readonly")
        self.combo_ev_categoria.set("Seleccione una categoría")
        self.combo_ev_categoria.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Ubicación").pack(anchor="w", padx=10, pady=(8, 2)) #Agregado por Jimena por el RF-09
        self.combo_ev_ubicacion = ctk.CTkComboBox(form, values=["Seleccione una ubicación"], state="readonly")
        self.combo_ev_ubicacion.set("Seleccione una ubicación")
        self.combo_ev_ubicacion.pack(fill="x", padx=10, pady=4)



        ctk.CTkLabel(form, text="Inicio").pack(anchor="w", padx=10, pady=(10, 2))
        fila_inicio = ctk.CTkFrame(form, fg_color="transparent"); fila_inicio.pack(fill="x", padx=10)
        self.fecha_inicio = self.crear_selector_fecha(fila_inicio)
        self.fecha_inicio.pack(side="left", fill="x", expand=True)
        self.hora_inicio = ctk.CTkEntry(fila_inicio, placeholder_text="HH:MM", width=75)
        self.hora_inicio.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(form, text="Fin").pack(anchor="w", padx=10, pady=(10, 2))
        fila_fin = ctk.CTkFrame(form, fg_color="transparent"); fila_fin.pack(fill="x", padx=10)
        self.fecha_fin = self.crear_selector_fecha(fila_fin)
        self.fecha_fin.pack(side="left", fill="x", expand=True)
        self.hora_fin = ctk.CTkEntry(fila_fin, placeholder_text="HH:MM", width=75)
        self.hora_fin.pack(side="left", padx=(6, 0))

        ctk.CTkButton(form, text="➕ Crear evento", command=self.agregar_evento).pack(fill="x", padx=10, pady=(16, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionado", command=self.actualizar_evento).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nuevo / Limpiar", command=self.limpiar_form_evento, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionado", command=self.eliminar_evento, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        self.limpiar_form_evento()

    def crear_selector_fecha(self, parent):
        if DateEntry is not None:
            return DateEntry(parent, date_pattern="yyyy-mm-dd", font=("Arial", 10))
        return ttk.Entry(parent)

    def obtener_fecha(self, widget):
        if DateEntry is not None:
            return widget.get_date().strftime("%Y-%m-%d")
        return widget.get().strip()

    def establecer_fecha(self, widget, valor):
        fecha = valor.date() if hasattr(valor, "date") else datetime.strptime(str(valor)[:10], "%Y-%m-%d").date()
        if DateEntry is not None:
            widget.set_date(fecha)
        else:
            widget.delete(0, tk.END); widget.insert(0, fecha.strftime("%Y-%m-%d"))

    def evento_seleccionado_id(self):
        sel = self.tree_eventos.selection()
        return self.tree_eventos.item(sel[0])["values"][0] if sel else None

    def cargar_evento_seleccionado(self, _=None):
        sel = self.tree_eventos.selection()
        if not sel: return
        vals = self.tree_eventos.item(sel[0])["values"]
        self.entry_ev_titulo.delete(0, tk.END); self.entry_ev_titulo.insert(0, vals[3])
        self.combo_ev_usuario.set(vals[1])
        self.combo_ev_categoria.set(vals[2])
        self.combo_ev_ubicacion.set(vals[3] if len(vals) > 6 and vals[3] else "Seleccione una ubicación")  #Agregado por Jimena por el RF-09
        try:
            ini = datetime.strptime(str(vals[5]), "%Y-%m-%d %H:%M")
            fin = datetime.strptime(str(vals[6]), "%Y-%m-%d %H:%M")
            self.establecer_fecha(self.fecha_inicio, ini)
            self.establecer_fecha(self.fecha_fin, fin)
            self.hora_inicio.delete(0, tk.END); self.hora_inicio.insert(0, ini.strftime("%H:%M"))
            self.hora_fin.delete(0, tk.END); self.hora_fin.insert(0, fin.strftime("%H:%M"))
        except ValueError:
            pass

    def limpiar_form_evento(self):
        self.tree_eventos.selection_remove(self.tree_eventos.selection())
        self.entry_ev_titulo.delete(0, tk.END)
        self.combo_ev_usuario.set("Seleccione un usuario")
        self.combo_ev_categoria.set("Seleccione una categoría")
        hoy = datetime.now()
        self.establecer_fecha(self.fecha_inicio, hoy); self.establecer_fecha(self.fecha_fin, hoy)
        self.hora_inicio.delete(0, tk.END); self.hora_inicio.insert(0, "09:00")
        self.hora_fin.delete(0, tk.END); self.hora_fin.insert(0, "10:00")
        self.combo_ev_ubicacion.set("Seleccione una ubicación")  #Agregado por Jimena por el RF-09

    def datos_evento_formulario(self):
        titulo = self.entry_ev_titulo.get().strip()
        usuario = self.usuarios_combo.get(self.combo_ev_usuario.get())
        categoria = self.categorias_combo.get(self.combo_ev_categoria.get())
        ubicacion = self.ubicaciones_combo.get(self.combo_ev_ubicacion.get()) #Agregado por Jimena por el RF-09
        try:
            inicio = datetime.strptime(f"{self.obtener_fecha(self.fecha_inicio)} {self.hora_inicio.get().strip()}", "%Y-%m-%d %H:%M")
            fin = datetime.strptime(f"{self.obtener_fecha(self.fecha_fin)} {self.hora_fin.get().strip()}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("La hora debe tener formato HH:MM, por ejemplo 09:30.")
        if not titulo or usuario is None or categoria is None:
            raise ValueError("Completa título, propietario y categoría.")
        if fin <= inicio:
            raise ValueError("La fecha y hora de finalización deben ser posteriores al inicio.")
        return usuario, categoria, ubicacion, titulo, inicio, fin

    def agregar_evento(self):
        try:
            usuario, categoria, ubicacion, titulo, inicio, fin = self.datos_evento_formulario() #Agregado por Jimena por el RF-09 (lo que hace esta funcion es que obtiene los datos de un formulario de eventos y los devuelve agrupados (generalmente en una tupla o lista). )
            datos = self.datos_evento_formulario()
            self.ejecutar_consulta("""
                INSERT INTO eventos
                (id_usuario_propietario, id_categoria, id_ubicacion, titulo, fecha_inicio, fecha_fin) 
                VALUES (%s, %s, %s, %s, %s,%s)
            """, (usuario, categoria, ubicacion, titulo, inicio, fin) ) #Agregado por Jimena por el RF-09
            self.limpiar_form_evento(); self.cargar_datos_eventos()
            messagebox.showinfo("Éxito", "Evento creado correctamente.")
        except Exception as e:
            messagebox.showerror("No se pudo crear el evento", str(e))

    def actualizar_evento(self):
        eid = self.evento_seleccionado_id()
        if eid is None: return messagebox.showwarning("Selección requerida", "Selecciona un evento.")
        try:
            usuario, categoria, ubicacion, titulo, inicio, fin = self.datos_evento_formulario()
            self.ejecutar_consulta("""
                UPDATE eventos SET id_usuario_propietario=%s, id_categoria=%s, id_ubicacion=%s,
                titulo=%s, fecha_inicio=%s, fecha_fin=%s WHERE id_evento=%s
            """, (usuario, categoria, ubicacion, titulo, inicio, fin, eid))
            self.cargar_datos_eventos(); messagebox.showinfo("Éxito", "Evento actualizado.")
        except psycopg2.errors.ExclusionViolation:
                messagebox.showerror("Conflicto de horario", "Ya existe un evento programado en esa ubicación durante ese horario.") #Agregado por Jimena por el RF-09
        except Exception as e:
            messagebox.showerror("No se pudo actualizar", str(e))

    def eliminar_evento(self):
        eid = self.evento_seleccionado_id()
        if eid is None: return messagebox.showwarning("Selección requerida", "Selecciona un evento.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar el evento seleccionado?"): return
        try:
            self.ejecutar_consulta("DELETE FROM eventos WHERE id_evento=%s", (eid,))
            self.limpiar_form_evento(); self.cargar_datos_eventos()
            messagebox.showinfo("Eliminado", "Evento eliminado.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_eventos(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT e.id_evento, u.id_usuario, u.nombre, u.apellido,
                       c.id_categoria, c.nombre, ub.id_ubicacion, ub.nombre, ub.ciudad, e.titulo, e.fecha_inicio, e.fecha_fin
                FROM eventos e
                JOIN usuarios u ON u.id_usuario = e.id_usuario_propietario
                JOIN categorias c ON c.id_categoria = e.id_categoria
                LEFT JOIN ubicaciones ub ON ub.id_ubicacion = e.id_ubicacion
                ORDER BY e.fecha_inicio DESC
            """, fetch=True)
            for item in self.tree_eventos.get_children(): self.tree_eventos.delete(item)
            for row in rows:
                usuario = f"{row[2]} {row[3]} — #{row[1]}"
                categoria = f"{row[5]} — #{row[4]}"
                ubicacion = f"{row[7]} — {row[8]} (#{row[6]})" if row[6] is not None else ""#Agregado por Jimena por el RF-09 y el resto de indices row se ajustaron porq ahora hay tres columnas (ub.id_ubicacion, ub.nombre, ub.ciudad)
                inicio = row[10].strftime("%Y-%m-%d %H:%M") if hasattr(row[10], "strftime") else row[10]
                fin = row[11].strftime("%Y-%m-%d %H:%M") if hasattr(row[11], "strftime") else row[11]
                self.tree_eventos.insert("", "end", values=(row[0], usuario, categoria,ubicacion, row[9], inicio, fin))

            valores_u = ["Seleccione un usuario"] + list(self.usuarios_combo.keys())
            valores_c = ["Seleccione una categoría"] + list(self.categorias_combo.keys())
            valores_ub = ["Seleccione una ubicación"] + list(self.ubicaciones_combo.keys()) #Agregado por Jimena por el RF-09
            self.combo_ev_usuario.configure(values=valores_u)
            self.combo_ev_categoria.configure(values=valores_c)
            self.combo_ev_ubicacion.configure(values=valores_ub) #Agregado por Jimena por el RF-09
        except Exception as e:
            print(f"Error cargando eventos: {e}")


##Agregado por Jimena por el RF-11 y RF-12 (este es para la pestaña de Disponibilidad )
    def configurar_pestana_disponibilidad(self):
        self.crear_encabezado(self.tab_disponibilidad, "Disponibilidad",
                               "Administrar los periodos libres u ocupados y consultar quién está disponible.")

        subtabs = ctk.CTkTabview(self.tab_disponibilidad)
        subtabs.pack(fill="both", expand=True, padx=10, pady=5)

        tab_gestion = subtabs.add("Gestión")
        tab_buscar = subtabs.add("Buscar disponibles")

        #SUB-PESTAÑA: Gestión (RF-11)
        cuerpo = ctk.CTkFrame(tab_gestion, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320); form.grid(row=0, column=1, sticky="nsew")

        self.tree_disponibilidades = self.crear_treeview(
            tabla, ("ID", "Usuario", "Fecha", "Inicio", "Fin", "Tipo"),
            (50, 160, 100, 80, 80, 110)
        )
        self.tree_disponibilidades.bind("<<TreeviewSelect>>", self.cargar_disponibilidad_seleccionada)

        ctk.CTkLabel(form, text="Formulario de disponibilidad", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        ctk.CTkLabel(form, text="Usuario").pack(anchor="w", padx=10, pady=(4, 2))
        self.combo_disp_usuario = ctk.CTkComboBox(form, values=["Seleccione un usuario"], state="readonly")
        self.combo_disp_usuario.set("Seleccione un usuario")
        self.combo_disp_usuario.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Fecha").pack(anchor="w", padx=10, pady=(8, 2))
        self.fecha_disp = self.crear_selector_fecha(form)
        self.fecha_disp.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Hora inicio (HH:MM)").pack(anchor="w", padx=10, pady=(8, 2))
        self.entry_disp_hora_inicio = ctk.CTkEntry(form, placeholder_text="09:00")
        self.entry_disp_hora_inicio.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Hora fin (HH:MM)").pack(anchor="w", padx=10, pady=(8, 2))
        self.entry_disp_hora_fin = ctk.CTkEntry(form, placeholder_text="11:00")
        self.entry_disp_hora_fin.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Tipo").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_disp_tipo = ctk.CTkComboBox(form, values=["Seleccione un tipo"], state="readonly")
        self.combo_disp_tipo.set("Seleccione un tipo")
        self.combo_disp_tipo.pack(fill="x", padx=10, pady=4)

        ctk.CTkButton(form, text="Registrar franja", command=self.agregar_disponibilidad).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="Actualizar seleccionada", command=self.actualizar_disponibilidad).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Nueva / Limpiar", command=self.limpiar_form_disponibilidad, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Eliminar seleccionada", command=self.eliminar_disponibilidad,
                      fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        # SUBPESTAÑA: Buscar disponibles (RF-12)
        buscar_frame = ctk.CTkFrame(tab_buscar, fg_color="transparent")
        buscar_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(buscar_frame, text="Buscar usuarios libres en un rango horario",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        fila_busqueda = ctk.CTkFrame(buscar_frame, fg_color="transparent")
        fila_busqueda.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(fila_busqueda, text="Fecha").pack(side="left", padx=(0, 5))
        self.fecha_busqueda = self.crear_selector_fecha(fila_busqueda)
        self.fecha_busqueda.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(fila_busqueda, text="Desde").pack(side="left", padx=(0, 5))
        self.entry_busqueda_inicio = ctk.CTkEntry(fila_busqueda, placeholder_text="14:00", width=70)
        self.entry_busqueda_inicio.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(fila_busqueda, text="Hasta").pack(side="left", padx=(0, 5))
        self.entry_busqueda_fin = ctk.CTkEntry(fila_busqueda, placeholder_text="16:00", width=70)
        self.entry_busqueda_fin.pack(side="left", padx=(0, 15))

        ctk.CTkButton(fila_busqueda, text="🔍 Buscar disponibles",
                      command=self.buscar_usuarios_disponibles).pack(side="left")

        self.tree_usuarios_disponibles = self.crear_treeview(
            buscar_frame, ("ID", "Nombre", "Apellido"), (60, 180, 180)
        )

# Para lo de CRUD  (RF-11)
    def disponibilidad_seleccionada_id(self):
        sel = self.tree_disponibilidades.selection()
        return self.tree_disponibilidades.item(sel[0])["values"][0] if sel else None

    def cargar_disponibilidad_seleccionada(self, _=None):
        sel = self.tree_disponibilidades.selection()
        if not sel: return
        vals = self.tree_disponibilidades.item(sel[0])["values"]
        self.combo_disp_usuario.set(vals[1])
        self.establecer_fecha(self.fecha_disp, str(vals[2]))
        self.entry_disp_hora_inicio.delete(0, tk.END); self.entry_disp_hora_inicio.insert(0, vals[3])
        self.entry_disp_hora_fin.delete(0, tk.END); self.entry_disp_hora_fin.insert(0, vals[4])
        self.combo_disp_tipo.set(vals[5])

    def limpiar_form_disponibilidad(self):
        self.tree_disponibilidades.selection_remove(self.tree_disponibilidades.selection())
        self.combo_disp_usuario.set("Seleccione un usuario")
        self.establecer_fecha(self.fecha_disp, datetime.now())
        self.entry_disp_hora_inicio.delete(0, tk.END)
        self.entry_disp_hora_fin.delete(0, tk.END)
        self.combo_disp_tipo.set("Seleccione un tipo")

    def _datos_disponibilidad_formulario(self):
        usuario = self.usuarios_combo.get(self.combo_disp_usuario.get())
        tipo = self.tipos_disponibilidad_combo.get(self.combo_disp_tipo.get())
        fecha = self.obtener_fecha(self.fecha_disp)
        hora_inicio = self.entry_disp_hora_inicio.get().strip()
        hora_fin = self.entry_disp_hora_fin.get().strip()
        if usuario is None or tipo is None:
            raise ValueError("Selecciona usuario y tipo de disponibilidad.")
        if not hora_inicio or not hora_fin:
            raise ValueError("Indica hora de inicio y de fin .")
        return usuario, fecha, hora_inicio, hora_fin, tipo

    def agregar_disponibilidad(self):
        try:
            datos = self._datos_disponibilidad_formulario()
            usuario, fecha, hora_inicio, hora_fin, tipo = datos
            self.ejecutar_consulta("""
                INSERT INTO disponibilidades (fecha, hora_inicio, hora_fin, id_usuario, id_tipo)
                VALUES (%s, %s, %s, %s, %s)
            """, (fecha, hora_inicio, hora_fin, usuario, tipo))
            self.limpiar_form_disponibilidad(); self.cargar_datos_disponibilidades()
            messagebox.showinfo("Éxito", "Disponibilidad registrada.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except psycopg2.errors.ExclusionViolation:
            messagebox.showerror("Conflicto de horario", "Este usuario ya tiene una disponibilidad que se cruza con ese horario.")
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))

    def actualizar_disponibilidad(self):
        did = self.disponibilidad_seleccionada_id()
        if did is None:
            return messagebox.showwarning("Selección requerida", "Selecciona una disponibilidad.")
        try:
            usuario, fecha, hora_inicio, hora_fin, tipo = self._datos_disponibilidad_formulario()
            self.ejecutar_consulta("""
                UPDATE disponibilidades SET fecha=%s, hora_inicio=%s, hora_fin=%s, id_usuario=%s, id_tipo=%s
                WHERE id_disponibilidad=%s
            """, (fecha, hora_inicio, hora_fin, usuario, tipo, did))
            self.cargar_datos_disponibilidades()
            messagebox.showinfo("Éxito", "Disponibilidad actualizada.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except psycopg2.errors.ExclusionViolation:
            messagebox.showerror("Conflicto de horario", "Este usuario ya tiene una disponibilidad que se cruza con ese horario.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_disponibilidad(self):
        did = self.disponibilidad_seleccionada_id()
        if did is None:
            return messagebox.showwarning("Selección requerida", "Selecciona una disponibilidad.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar la disponibilidad seleccionada?"):
            return
        try:
            self.ejecutar_consulta("DELETE FROM disponibilidades WHERE id_disponibilidad=%s", (did,))
            self.limpiar_form_disponibilidad(); self.cargar_datos_disponibilidades()
            messagebox.showinfo("Eliminado", "Disponibilidad eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_disponibilidades(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT d.id_disponibilidad, u.nombre || ' ' || u.apellido, d.fecha,
                       d.hora_inicio, d.hora_fin, t.nombre
                FROM disponibilidades d
                JOIN usuarios u ON u.id_usuario = d.id_usuario
                JOIN tipos_disponibilidad t ON t.id_tipo = d.id_tipo
                ORDER BY d.fecha DESC, d.hora_inicio
            """, fetch=True)
            for item in self.tree_disponibilidades.get_children():
                self.tree_disponibilidades.delete(item)
            for row in rows:
                self.tree_disponibilidades.insert("", "end", values=row)

            tipos = self.ejecutar_consulta("SELECT id_tipo, nombre FROM tipos_disponibilidad ORDER BY nombre", fetch=True)
            self.tipos_disponibilidad_combo = {nombre: tid for tid, nombre in tipos}
            self.combo_disp_tipo.configure(values=["Seleccione un tipo"] + list(self.tipos_disponibilidad_combo.keys()))

            valores_u = ["Seleccione un usuario"] + list(self.usuarios_combo.keys())
            self.combo_disp_usuario.configure(values=valores_u)
        except Exception as e:
            print(f"Error cargando disponibilidades: {e}")

#Para el panel analitico (RF-12)
    def buscar_usuarios_disponibles(self):
        fecha = self.obtener_fecha(self.fecha_busqueda)
        hora_inicio = self.entry_busqueda_inicio.get().strip()
        hora_fin = self.entry_busqueda_fin.get().strip()
        if not hora_inicio or not hora_fin:
            return messagebox.showwarning("Datos incompletos", "Indica hora de inicio y de fin (HH:MM).")
        try:
            inicio_dt = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
            fin_dt = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")
        except ValueError:
            return messagebox.showwarning("Formato inválido", "Usar el formato HH:MM")

        try:
            rows = self.ejecutar_consulta("""
                SELECT u.id_usuario, u.nombre, u.apellido
                FROM usuarios u
                WHERE u.activo = TRUE
                AND NOT EXISTS (
                    SELECT 1 FROM eventos e
                    WHERE (e.id_usuario_propietario = u.id_usuario
                           OR EXISTS (SELECT 1 FROM participaciones p
                                      WHERE p.id_evento = e.id_evento AND p.id_invitado = u.id_usuario))
                    AND tsrange(e.fecha_inicio, e.fecha_fin) && tsrange(%s::timestamp, %s::timestamp)
                )
                AND NOT EXISTS (
                    SELECT 1 FROM disponibilidades d
                    JOIN tipos_disponibilidad t ON t.id_tipo = d.id_tipo
                    WHERE d.id_usuario = u.id_usuario
                    AND d.fecha = %s::date
                    AND tsrange(d.fecha + d.hora_inicio, d.fecha + d.hora_fin) && tsrange(%s::timestamp, %s::timestamp)
                    AND t.nombre IN ('ocupado', 'no disponible')
                )
                ORDER BY u.nombre
            """, (inicio_dt, fin_dt, fecha, inicio_dt, fin_dt), fetch=True)

            for item in self.tree_usuarios_disponibles.get_children():
                self.tree_usuarios_disponibles.delete(item)
            if not rows:
                messagebox.showinfo("Sin resultados", "Ningún usuario está disponible en ese rango horario.")
                return
            for row in rows:
                self.tree_usuarios_disponibles.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error al buscar", str(e))

#Agregado por Jimena para modulo Tareas Asociadas a Eventos 
    def configurar_pestana_tareas (self): 
        self.crear_encabezado(self.tab_tareas, "Tareas", "Da seguimiento a las tareas asociadas a cada evento.")

        subtabs= ctk.CTkTabview(self.tab_tareas)
        subtabs.pack(fill="both", expand=True, padx=10, pady=5)

        tab_gestion = subtabs.add("Gestión")
        tab_metricas = subtabs.add("Métricas")
        tab_seguimiento = subtabs.add("Seguimiento")

        self.configurar_subpestana_metricas(tab_metricas)        # Agregado por Jimena para RF-17
        self.configurar_subpestana_seguimiento(tab_seguimiento)  #Agregado por Jimena para RF-16

        cuerpo = ctk.CTkFrame(tab_gestion, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=330); form.grid(row=0, column=1, sticky="nsew")

        self.tree_tareas = self.crear_treeview(
            tabla, ("ID", "Título", "Evento", "Responsable", "Prioridad", "Fecha límite", "Estado"),
             (50, 150, 150, 150, 90, 100, 100))
        
        self.tree_tareas.bind("<<TreeviewSelect>>", self.cargar_tarea_seleccionada)

        ctk.CTkLabel(form, text="Formulario de tarea", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        
        self.entry_tarea_titulo = ctk.CTkEntry(form, placeholder_text="Título de la tarea")
        self.entry_tarea_titulo.pack(fill="x", padx=10, pady=6)


        self.entry_tarea_descripcion = ctk.CTkEntry(form, placeholder_text="Descripción")
        self.entry_tarea_descripcion.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Evento").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_tarea_evento = ctk.CTkComboBox(form, values=["Seleccione un evento"], state="readonly")
        self.combo_tarea_evento.set("Seleccione un evento")
        self.combo_tarea_evento.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Usuario responsable").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_tarea_usuario = ctk.CTkComboBox(form, values=["Seleccione un usuario"], state="readonly")
        self.combo_tarea_usuario.set("Seleccione un usuario")
        self.combo_tarea_usuario.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Prioridad").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_tarea_prioridad = ctk.CTkComboBox(form, values=["baja", "media", "alta"], state="readonly")
        self.combo_tarea_prioridad.set("media")
        self.combo_tarea_prioridad.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Fecha límite").pack(anchor="w", padx=10, pady=(8, 2))
        self.fecha_tarea_limite = self.crear_selector_fecha(form)
        self.fecha_tarea_limite.pack(fill="x", padx=10, pady=4)


        ctk.CTkLabel(form, text="Estado").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_tarea_estado = ctk.CTkComboBox(
            form, values=["pendiente", "en_progreso", "completada", "cancelada"], state="readonly"
        )
        self.combo_tarea_estado.set("pendiente")
        self.combo_tarea_estado.pack(fill="x", padx=10, pady=4)

        ctk.CTkButton(form, text="Registrar tarea", command=self.agregar_tarea).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="Actualizar seleccionada", command=self.actualizar_tarea).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Nueva / Limpiar", command=self.limpiar_form_tarea, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="Eliminar seleccionada", command=self.eliminar_tarea,
                      fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)


#Métodos CRUD
    def tarea_seleccionada_id(self):
        sel = self.tree_tareas.selection()
        return self.tree_tareas.item(sel[0])["values"][0] if sel else None

    def cargar_tarea_seleccionada (self, _=None):
        sel = self.tree_tareas.selection()
        if not sel: return
        vals = self.tree_tareas.item(sel[0])["values"]
        self.entry_tarea_titulo.delete(0, tk.END); self.entry_tarea_titulo.insert(0, vals[1])
        self.combo_tarea_evento.set(vals[2])
        self.combo_tarea_usuario.set(vals[3])
        self.combo_tarea_prioridad.set(vals[4])
        self.establecer_fecha(self.fecha_tarea_limite, str(vals[5]))
        self.combo_tarea_estado.set(vals[6])

    def limpiar_form_tarea(self):
        self.tree_tareas.selection_remove(self.tree_tareas.selection())
        self.entry_tarea_titulo.delete(0, tk.END)
        self.entry_tarea_descripcion.delete(0, tk.END)
        self.combo_tarea_evento.set("Seleccione un evento")
        self.combo_tarea_usuario.set("Seleccione un usuario")
        self.combo_tarea_prioridad.set("media")
        self.establecer_fecha(self.fecha_tarea_limite, datetime.now())
        self.combo_tarea_estado.set("pendiente")

    def _datos_tarea_formulario(self):
        titulo = self.entry_tarea_titulo.get().strip()
        descripcion = self.entry_tarea_descripcion.get().strip()
        evento = self.eventos_combo.get(self.combo_tarea_evento.get())
        usuario = self.usuarios_combo.get(self.combo_tarea_usuario.get())
        prioridad = self.combo_tarea_prioridad.get()
        fecha_limite = self.obtener_fecha(self.fecha_tarea_limite)
        estado = self.combo_tarea_estado.get()
        if not titulo or evento is None or usuario is None:
            raise ValueError("Completa título, evento y usuario responsable.")
        return titulo, descripcion, prioridad, fecha_limite, estado, usuario, evento

    def agregar_tarea(self):
        try:
            datos = self._datos_tarea_formulario()
            self.ejecutar_consulta("""
                INSERT INTO tareas (titulo, descripcion, prioridad, fecha_limite, estados, id_usuario, id_evento)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, datos)
            self.limpiar_form_tarea(); self.cargar_datos_tareas()
            messagebox.showinfo("Éxito", "Tarea registrada correctamente.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))

    def actualizar_tarea(self):
        tid = self.tarea_seleccionada_id()
        if tid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona una tarea.")
        try:
            titulo, descripcion, prioridad, fecha_limite, estado, usuario, evento = self._datos_tarea_formulario()
            self.ejecutar_consulta("""
                UPDATE tareas SET titulo=%s, descripcion=%s, prioridad=%s, fecha_limite=%s,
                estados=%s, id_usuario=%s, id_evento=%s WHERE id_tarea=%s
            """, (titulo, descripcion, prioridad, fecha_limite, estado, usuario, evento, tid))
            self.cargar_datos_tareas()
            messagebox.showinfo("Éxito", "Tarea actualizada.")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_tarea(self):
            tid = self.tarea_seleccionada_id()
            if tid is None:
                return messagebox.showwarning("Selección requerida", "Selecciona una tarea.")
            if not messagebox.askyesno("Confirmar", "¿Eliminar la tarea seleccionada?"):
                return
            try:
                self.ejecutar_consulta("DELETE FROM tareas WHERE id_tarea=%s", (tid,))
                self.limpiar_form_tarea(); self.cargar_datos_tareas()
                messagebox.showinfo("Eliminado", "Tarea eliminada.")
            except Exception as e:
                messagebox.showerror("No se pudo eliminar", str(e))


    def cargar_datos_tareas(self):
            try:
                rows = self.ejecutar_consulta("""
                    SELECT t.id_tarea, t.titulo, e.titulo, u.nombre || ' ' || u.apellido,
                        t.prioridad, t.fecha_limite, t.estados
                    FROM tareas t
                    JOIN eventos e ON e.id_evento = t.id_evento
                    JOIN usuarios u ON u.id_usuario = t.id_usuario
                    ORDER BY t.fecha_limite
                """, fetch=True)
                for item in self.tree_tareas.get_children():
                    self.tree_tareas.delete(item)
                for row in rows:
                    self.tree_tareas.insert("", "end", values=row)

                eventos = self.ejecutar_consulta("SELECT id_evento, titulo FROM eventos ORDER BY titulo", fetch=True)
                self.eventos_combo = {titulo: eid for eid, titulo in eventos}
                self.combo_tarea_evento.configure(values=["Seleccione un evento"] + list(self.eventos_combo.keys()))

                valores_u = ["Seleccione un usuario"] + list(self.usuarios_combo.keys())
                self.combo_tarea_usuario.configure(values=valores_u)
            except Exception as e:
                            print(f"Error cargando tareas: {e}")

#Agregado por Jimena para RF-17 (Reporte de carga de trabajo y tareas pendientes por usuario)

    def configurar_subpestana_metricas(self, tab_metricas):
            self.crear_encabezado(
                tab_metricas, "Carga de trabajo por usuario",
                "Volumen de tareas activas (pendiente / en progreso) y tareas vencidas por cada responsable."
            )

            contenedor = ctk.CTkFrame(tab_metricas, fg_color="transparent")
            contenedor.pack(fill="both", expand=True, padx=10, pady=5)

            ctk.CTkButton(
                contenedor, text="🔄 Actualizar métricas", command=self.cargar_metricas_tareas
            ).pack(anchor="w", padx=5, pady=(0, 10))

            self.tree_metricas_tareas = self.crear_treeview(
            contenedor,
            ("Usuario", "Tareas activas", "Tareas vencidas", "Total asignadas"),
            (260, 130, 130, 130)
        )

    def cargar_metricas_tareas(self):
            try:
                rows = self.ejecutar_consulta("""
                    SELECT u.nombre || ' ' || u.apellido AS usuario,
                        COUNT(*) FILTER (
                            WHERE t.estados IN ('pendiente', 'en_progreso')
                        ) AS tareas_activas,
                        COUNT(*) FILTER (
                            WHERE t.estados IN ('pendiente', 'en_progreso')
                            AND t.fecha_limite < CURRENT_DATE
                        ) AS tareas_vencidas,
                        COUNT(t.id_tarea) AS total_asignadas
                    FROM usuarios u
                    LEFT JOIN tareas t ON t.id_usuario = u.id_usuario
                    GROUP BY u.id_usuario, u.nombre, u.apellido
                    ORDER BY tareas_vencidas DESC, tareas_activas DESC, usuario
                """, fetch=True)

                for item in self.tree_metricas_tareas.get_children():
                    self.tree_metricas_tareas.delete(item)
                for row in rows:
                    self.tree_metricas_tareas.insert("", "end", values=row)
            except Exception as e:
                print(f"Error cargando métricas de tareas: {e}")

#Agregado por Jimena para RF-16 (Carga de trabajo y vencimiento, eventos con tareas vencidas)

    def configurar_subpestana_seguimiento(self, tab_seguimiento):
            self.crear_encabezado(
                tab_seguimiento, "Eventos con tareas vencidas",
                "Eventos que arrastran tareas fuera de su fecha límite (pendientes o en progreso y ya vencidas)."
            )

            contenedor = ctk.CTkFrame(tab_seguimiento, fg_color="transparent")
            contenedor.pack(fill="both", expand=True, padx=10, pady=5)

            ctk.CTkButton(
                contenedor, text="🔄 Actualizar seguimiento", command=self.cargar_eventos_con_tareas_vencidas
            ).pack(anchor="w", padx=5, pady=(0, 10))

            self.tree_eventos_vencidos = self.crear_treeview(
                contenedor,
                ("Evento", "Fin del evento", "Tareas vencidas", "Responsables"),
                (220, 150, 120, 260)
        )

    def cargar_eventos_con_tareas_vencidas(self):
            try:
                rows = self.ejecutar_consulta("""
                    SELECT e.titulo AS evento,
                        e.fecha_fin,
                        COUNT(t.id_tarea) AS tareas_vencidas,
                        STRING_AGG(DISTINCT u.nombre || ' ' || u.apellido, ', ') AS responsables
                    FROM tareas t
                    JOIN eventos e ON e.id_evento = t.id_evento
                    JOIN usuarios u ON u.id_usuario = t.id_usuario
                    WHERE t.estados IN ('pendiente', 'en_progreso')
                    AND t.fecha_limite < CURRENT_DATE
                    GROUP BY e.id_evento, e.titulo, e.fecha_fin
                    ORDER BY tareas_vencidas DESC, e.fecha_fin ASC
                """, fetch=True)

                for item in self.tree_eventos_vencidos.get_children():
                    self.tree_eventos_vencidos.delete(item)
                if not rows:
                    return
                for row in rows:
                    titulo, fecha_fin, vencidas, responsables = row
                    fecha_fin = fecha_fin.strftime("%Y-%m-%d %H:%M") if hasattr(fecha_fin, "strftime") else fecha_fin
                    self.tree_eventos_vencidos.insert("", "end", values=(titulo, fecha_fin, vencidas, responsables))
            except Exception as e:
                print(f"Error cargando eventos con tareas vencidas: {e}")





    # -------------------- REFRESCO GENERAL --------------------

    def actualizar_todas_las_tablas(self):
        self.cargar_datos_usuarios()
        self.cargar_datos_categorias()
        self.cargar_datos_ubicaciones() #Agregado por Jimena por el RF-08 (se pone primero porq sino no carga)
        self.cargar_datos_disponibilidades() #Agregado por Jimena por el RF-11 y RF-12
        self.cargar_datos_tareas()
        self.cargar_datos_eventos()
        self.cargar_metricas_tareas()             #Agregado por Jimena por el RF-17
        self.cargar_eventos_con_tareas_vencidas()  #Agregado por Jimena por el RF-16
    
        

if __name__ == "__main__":
    app = AppAgenda()
    app.mainloop()

