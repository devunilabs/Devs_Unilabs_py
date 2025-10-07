 ## FUNCIONANDO CORRECTAMENTE  USAR ##
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Configuración de estilo
STYLE = {
    "font": {"normal": ("Segoe UI", 10), "bold": ("Segoe UI", 10, "bold"), "title": ("Segoe UI", 11, "bold")},
    "colors": {
        "primary": "#0056b3",
        "secondary": "#003366",
        "background": "#f8f9fa",
        "text": "#333333",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#17a2b8",
        "border": "#dee2e6"
    },
    "logo": {"path": "unilabs_logo.jpg", "max_width": 180},
    "app": {"title": "Transformador TAT CSV - UNILABS", "min_size": (800, 600)}
}

@dataclass
class FileResult:
    filename: str
    success: bool
    transformed: bool
    message: str

class CSVProcessor:
    """Maneja todas las operaciones de procesamiento de CSV"""
    @staticmethod
    def transform(content: str) -> Tuple[str, bool]:
        """Aplica transformaciones al contenido"""
        transformations = [
            ('|tubodemo', '|tubo|demo'),
            ('|tuboNro Episodio|', '|tubo|Nro Episodio|')
        ]
        new_content = content
        changes_made = False
        
        for old, new in transformations:
            if old in new_content:
                new_content = new_content.replace(old, new)
                changes_made = True
                
        return new_content, changes_made

    @staticmethod
    def read_file(path: str) -> Tuple[Optional[str], Optional[str]]:
        """Intenta leer un archivo con diferentes codificaciones"""
        encodings = ['utf-8-sig', 'latin-1', 'utf-16', 'windows-1252']
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read(), encoding
            except UnicodeDecodeError:
                continue
        return None, None

    @staticmethod
    def write_file(path: str, content: str, encoding: str) -> bool:
        """Escribe el archivo con la codificación especificada"""
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False

class ModernUI(tk.Tk):
    """Interfaz gráfica moderna para la aplicación"""
    def __init__(self):
        super().__init__()
        self.title(STYLE["app"]["title"])
        self.minsize(*STYLE["app"]["min_size"])
        self.configure(bg=STYLE["colors"]["background"])
        self.results: List[FileResult] = []
        
        # Configuración de estilos
        self._setup_styles()
        self._build_ui()
        
    def _setup_styles(self):
        """Configura estilos personalizados para widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para la barra de progreso
        style.configure("TProgressbar",
                       thickness=20,
                       troughcolor=STYLE["colors"]["border"],
                       background=STYLE["colors"]["primary"],
                       bordercolor=STYLE["colors"]["border"])
        
        # Estilo para los frames
        style.configure("TFrame", background=STYLE["colors"]["background"])
        
    def _build_ui(self):
        """Construye todos los componentes de la interfaz"""
        self._create_header()
        self._create_main_panel()
        self._create_progress_panel()
        self._create_results_panel()
        
    def _create_header(self):
        """Crea la cabecera con el logo y título"""
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Logo UNILABS
        try:
            logo_path = STYLE["logo"]["path"]
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                original_width, original_height = logo_img.size
                new_width = STYLE["logo"]["max_width"]
                new_height = int((new_width / original_width) * original_height)
                logo_img = logo_img.resize((new_width, new_height), Image.LANCZOS)
                
                self.logo_img = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=self.logo_img, bg=STYLE["colors"]["background"])
                logo_label.pack(side=tk.LEFT)
            else:
                raise FileNotFoundError(f"No se encontró el archivo de logo: {logo_path}")
        except Exception as e:
            print(f"Error cargando el logo: {e}")
            logo_label = tk.Label(header_frame, text="UNILABS", font=("Segoe UI", 16, "bold"),
                                fg=STYLE["colors"]["primary"], bg=STYLE["colors"]["background"])
            logo_label.pack(side=tk.LEFT)
        
        # Título de la aplicación
        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text="Transformador TAT CSV", 
                font=("Segoe UI", 14, "bold"), bg=STYLE["colors"]["background"],
                fg=STYLE["colors"]["primary"]).pack(anchor='e')
        
        tk.Label(title_frame, text="Versión 1.0", 
                font=STYLE["font"]["normal"], bg=STYLE["colors"]["background"],
                fg=STYLE["colors"]["text"]).pack(anchor='e')
    
    def _create_main_panel(self):
        """Crea el panel principal con instrucciones y botón"""
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Panel de instrucciones
        instr_frame = ttk.LabelFrame(main_frame, text=" INSTRUCCIONES ", style="TFrame",
                                   labelanchor="n", padding=(10, 5))
        instr_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(instr_frame, text="Este aplicativo realiza las siguientes transformaciones exactas:",
                font=STYLE["font"]["normal"], bg=STYLE["colors"]["background"],
                fg=STYLE["colors"]["text"], justify=tk.LEFT).pack(anchor='w')
        
        tk.Label(instr_frame, text="1. |tubodemo0| → |tubo|demo0|",
                font=STYLE["font"]["normal"], bg=STYLE["colors"]["background"],
                fg=STYLE["colors"]["primary"], justify=tk.LEFT).pack(anchor='w', padx=20)
        
        tk.Label(instr_frame, text="2. |tuboNro Episodio| → |tubo|Nro Episodio|",
                font=STYLE["font"]["normal"], bg=STYLE["colors"]["background"],
                fg=STYLE["colors"]["primary"], justify=tk.LEFT).pack(anchor='w', padx=20)
        
        # Botón de acción principal
        action_btn = tk.Button(main_frame, text="SELECCIONAR ARCHIVOS CSV", 
                             command=self._select_files,
                             bg=STYLE["colors"]["primary"],
                             fg="white",
                             font=("Segoe UI", 11, "bold"),
                             relief=tk.FLAT,
                             padx=20,
                             pady=10,
                             bd=0,
                             activebackground=STYLE["colors"]["secondary"],
                             activeforeground="white")
        action_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Bind hover effects
        action_btn.bind("<Enter>", lambda e: action_btn.config(bg=STYLE["colors"]["secondary"]))
        action_btn.bind("<Leave>", lambda e: action_btn.config(bg=STYLE["colors"]["primary"]))
    
    def _create_progress_panel(self):
        """Crea el panel de progreso y estadísticas"""
        progress_frame = ttk.Frame(self, style="TFrame")
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Información de tiempo
        time_frame = ttk.Frame(progress_frame, style="TFrame")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(time_frame, text="Inicio:", font=STYLE["font"]["bold"],
                bg=STYLE["colors"]["background"], fg=STYLE["colors"]["text"]).pack(side=tk.LEFT)
        
        self.start_time = tk.Label(time_frame, text="--:--:--", font=STYLE["font"]["normal"],
                                 bg=STYLE["colors"]["background"], fg=STYLE["colors"]["text"])
        self.start_time.pack(side=tk.LEFT, padx=5)
        
        tk.Label(time_frame, text="Fin:", font=STYLE["font"]["bold"],
                bg=STYLE["colors"]["background"], fg=STYLE["colors"]["text"]).pack(side=tk.LEFT, padx=(20, 0))
        
        self.end_time = tk.Label(time_frame, text="--:--:--", font=STYLE["font"]["normal"],
                               bg=STYLE["colors"]["background"], fg=STYLE["colors"]["text"])
        self.end_time.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Etiqueta de estado
        self.status = tk.Label(progress_frame, text="Esperando selección de archivos...",
                             font=STYLE["font"]["normal"], bg=STYLE["colors"]["background"],
                             fg=STYLE["colors"]["info"])
        self.status.pack(fill=tk.X)
    
    def _create_results_panel(self):
        """Crea el panel de resultados con lista de archivos"""
        results_frame = ttk.LabelFrame(self, text=" RESULTADOS ", style="TFrame",
                                     labelanchor="n", padding=(10, 5))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Contador de archivos
        self.counter = tk.Label(results_frame, text="Archivos procesados: 0",
                              font=STYLE["font"]["bold"], bg=STYLE["colors"]["background"],
                              fg=STYLE["colors"]["text"])
        self.counter.pack(anchor='w', pady=(0, 5))
        
        # Lista de archivos con scrollbar
        scroll_frame = ttk.Frame(results_frame, style="TFrame")
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_list = tk.Listbox(
            scroll_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            bg="white",
            fg=STYLE["colors"]["text"],
            selectbackground=STYLE["colors"]["primary"],
            selectforeground="white",
            relief=tk.FLAT,
            highlightthickness=0,
            activestyle="none"
        )
        self.results_list.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.results_list.yview)
    
    def _select_files(self):
        """Maneja la selección de archivos"""
        filetypes = [("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        if files := filedialog.askopenfilenames(title="Seleccionar archivos CSV", filetypes=filetypes):
            self._reset_ui()
            threading.Thread(target=self._process_files, args=(files,), daemon=True).start()
    
    def _reset_ui(self):
        """Resetea la UI para un nuevo proceso"""
        self.start_time.config(text=datetime.now().strftime('%H:%M:%S'))
        self.end_time.config(text="--:--:--")
        self.results_list.delete(0, tk.END)
        self.counter.config(text="Archivos procesados: 0")
        self.results = []
        self.progress["value"] = 0
        self.status.config(text="Preparando para procesar archivos...", fg=STYLE["colors"]["info"])
    
    def _process_files(self, files: List[str]):
        """Procesa todos los archivos seleccionados"""
        total_files = len(files)
        
        for i, file_path in enumerate(files, 1):
            self._update_progress(f"Procesando archivo {i}/{total_files}", i, total_files)
            result = self._process_single_file(file_path)
            self.results.append(result)
            self._add_result_to_list(result)
            self.counter.config(text=f"Archivos procesados: {i}/{total_files}")
        
        self._finish_processing(total_files)
    
    def _process_single_file(self, file_path: str) -> FileResult:
        """Procesa un único archivo y devuelve el resultado"""
        filename = os.path.basename(file_path)
        content, encoding = CSVProcessor.read_file(file_path)
        
        if content is None:
            return FileResult(filename, False, False, "Error: No se pudo leer el archivo")
        
        new_content, changes_made = CSVProcessor.transform(content)
        
        if not changes_made:
            return FileResult(filename, True, False, "Sin cambios necesarios")
        
        if CSVProcessor.write_file(file_path, new_content, encoding):
            return FileResult(filename, True, True, "Transformación exitosa")
        else:
            return FileResult(filename, False, False, "Error al guardar cambios")
    
    def _add_result_to_list(self, result: FileResult):
        """Añade un resultado a la lista con formato adecuado"""
        if not result.success:
            color = STYLE["colors"]["error"]
            prefix = "✗ ERROR:"                 
        elif result.transformed:
            color = STYLE["colors"]["success"]
            prefix = "✓ ÉXITO:"
        else:
            color = STYLE["colors"]["info"]
            prefix = "☑ INFO:"
        
        self.results_list.insert(tk.END, f"{prefix} {result.filename} - {result.message}")
        self.results_list.itemconfig(tk.END, {'fg': color})
    
    def _update_progress(self, message: str, current: int, total: int):
        """Actualiza la barra de progreso y mensaje de estado"""
        progress = int((current / total) * 100)
        
        self.after(0, lambda: self.__update_progress_ui(message, progress))
    
    def __update_progress_ui(self, message: str, progress: int):
        """Actualiza la UI del progreso (debe ejecutarse en el hilo principal)"""
        self.progress["value"] = progress
        
        if progress < 30:
            color = STYLE["colors"]["error"]
        elif progress < 70:
            color = STYLE["colors"]["warning"]
        else:
            color = STYLE["colors"]["success"]
        
        self.status.config(text=f"{progress}% - {message}", fg=color)
    
    def _finish_processing(self, total_files: int):
        """Muestra los resultados finales del procesamiento"""
        self.end_time.config(text=datetime.now().strftime('%H:%M:%S'))
        self._update_progress("Proceso completado", 100, 100)
        
        success = sum(1 for r in self.results if r.success and r.transformed)
        no_changes = sum(1 for r in self.results if r.success and not r.transformed)
        errors = sum(1 for r in self.results if not r.success)
        
        # Mostrar resumen en la lista
        self.results_list.insert(tk.END, "")
        self.results_list.insert(tk.END, "═" * 80)
        self.results_list.insert(tk.END, f"RESUMEN: {success} transformados | {no_changes} sin cambios | {errors} errores")
        self.results_list.itemconfig(tk.END, {'fg': STYLE["colors"]["primary"]})
        
        # Mostrar mensaje emergente
        messagebox.showinfo(
            "Proceso completado",
            f"Resultados del procesamiento:\n\n"
            f"• Archivos transformados correctamente: {success}\n"
            f"• Archivos sin cambios necesarios: {no_changes}\n"
            f"• Archivos con errores: {errors}",
            parent=self
        )

if __name__ == "__main__":
    # Verificación del logo antes de iniciar
    logo_path = STYLE["logo"]["path"]
    if not os.path.exists(logo_path):
        print(f"Advertencia: No se encontró el archivo de logo en {os.path.abspath(logo_path)}")
        print("Se mostrará texto en su lugar")
    
    app = ModernUI()
    app.mainloop()