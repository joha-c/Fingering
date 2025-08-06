import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
import time
import re

class TypingTutorApp:
    def __init__(self, master):
        self.master = master
        master.title("Entrenador de Tipeo Pro")
        master.geometry("1400x900")
        master.configure(bg="#1a1a1a")  # Fondo oscuro moderno
        master.minsize(1200, 800)

        # Configurar el estilo de ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.source_text = ""
        self.start_time = None
        self.timer_running = False
        self.max_time_seconds = 4 * 60
        self.selected_time = 4
        self.word_count = 0
        self.target_wpm = 0

        self.create_widgets()
        self.reset_session()

    def configure_styles(self):
        """Configurar estilos personalizados para ttk"""
        # Estilo para LabelFrame
        self.style.configure("Custom.TLabelframe", 
                           background="#2d2d2d",
                           borderwidth=2,
                           relief="solid")
        self.style.configure("Custom.TLabelframe.Label",
                           background="#2d2d2d",
                           foreground="#ffffff",
                           font=("Segoe UI", 11, "bold"))
        
        # Estilo para botones
        self.style.configure("Accent.TButton",
                           background="#0078d4",
                           foreground="white",
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           focuscolor="none")
        self.style.map("Accent.TButton",
                     background=[('active', '#106ebe')])

    def create_widgets(self):
        # Frame principal con gradiente visual
        main_container = tk.Frame(self.master, bg="#1a1a1a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header con título elegante
        header_frame = tk.Frame(main_container, bg="#1a1a1a", height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, 
                              text="⚡ Entrenador de Tipeo Pro", 
                              font=("Segoe UI", 18, "bold"), 
                              fg="#00d4ff", 
                              bg="#1a1a1a")
        title_label.pack(pady=10)

        subtitle_label = tk.Label(header_frame,
                                 text="Mejora tu velocidad y precisión de escritura",
                                 font=("Segoe UI", 10),
                                 fg="#b0b0b0",
                                 bg="#1a1a1a")
        subtitle_label.pack()

        # Canvas con scroll mejorado
        canvas = tk.Canvas(main_container, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Binding para la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # También bindear el scroll al frame para que funcione cuando el mouse esté sobre cualquier widget
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Configuración de Tiempo con diseño moderno ---
        time_frame = tk.Frame(scrollable_frame, bg="#2d2d2d", relief="solid", bd=1)
        time_frame.pack(fill=tk.X, pady=(0, 5), padx=5)

        time_header = tk.Frame(time_frame, bg="#2d2d2d", height=40)
        time_header.pack(fill=tk.X, padx=15, pady=(5, 2))
        
        time_title = tk.Label(time_header, text="⏰ Configuración de Tiempo", 
                             font=("Segoe UI", 8, "bold"), fg="#00d4ff", bg="#2d2d2d")
        time_title.pack(anchor="w")

        self.time_var = tk.IntVar(value=4)
        
        time_buttons_frame = tk.Frame(time_frame, bg="#2d2d2d")
        time_buttons_frame.pack(pady=5, padx=15)

        # Botones de tiempo con estilo moderno
        for i, (text, value) in enumerate([("1 minuto", 1), ("4 minutos", 4), ("Personalizado", 0)]):
            btn_frame = tk.Frame(time_buttons_frame, bg="#2d2d2d")
            btn_frame.pack(side=tk.LEFT, padx=10)
            
            radio = tk.Radiobutton(btn_frame, text=text, variable=self.time_var, value=value,
                                 command=self.update_time_selection, 
                                 font=("Segoe UI", 8),
                                 bg="#2d2d2d", fg="#ffffff", 
                                 activebackground="#2d2d2d", activeforeground="#00d4ff",
                                 selectcolor="#0078d4")
            radio.pack()

        self.custom_time_button = tk.Button(time_buttons_frame, text="Establecer Tiempo", 
                                          command=self.set_custom_time, 
                                          font=("Segoe UI", 8, "bold"), 
                                          bg="#ff6b35", fg="white", 
                                          activebackground="#e55a2b", 
                                          relief="flat", bd=0, cursor="hand2", 
                                          state=tk.DISABLED, padx=15, pady=5)
        self.custom_time_button.pack(side=tk.LEFT, padx=15)

        self.selected_time_label = tk.Label(time_frame, text="Tiempo seleccionado: 4 minutos", 
                                          font=("Segoe UI", 8, "bold"), fg="#00ff88", bg="#2d2d2d")
        self.selected_time_label.pack(pady=(3, 15))

        # --- Área para pegar texto con diseño mejorado ---
        paste_frame = tk.Frame(scrollable_frame, bg="#2d2d2d", relief="solid", bd=1)
        paste_frame.pack(fill=tk.X, pady=(0, 15), padx=5)

        paste_header = tk.Frame(paste_frame, bg="#2d2d2d")
        paste_header.pack(fill=tk.X, padx=15, pady=(3, 5))

        paste_title = tk.Label(paste_header, text="📝 Cargar Texto de Práctica", 
                              font=("Segoe UI", 8, "bold"), fg="#00d4ff", bg="#2d2d2d")
        paste_title.pack(anchor="w")

        self.paste_text_area = scrolledtext.ScrolledText(paste_frame, wrap=tk.WORD, width=60, height=4, 
                                                        font=("Consolas", 12), 
                                                        bg="#1a1a1a", fg="#ffffff",
                                                        insertbackground="#00d4ff",
                                                        selectbackground="#0078d4",
                                                        selectforeground="#ffffff",
                                                        relief="flat", bd=5)
        self.paste_text_area.pack(fill=tk.X, pady=7, padx=15)

        load_button = tk.Button(paste_frame, text="🚀 Cargar Texto para Practicar", 
                               command=self.load_text, 
                               font=("Segoe UI", 8, "bold"), 
                               bg="#00ff88", fg="#1a1a1a", 
                               activebackground="#00e577", 
                               relief="flat", bd=0, cursor="hand2",
                               padx=20, pady=5)
        load_button.pack(pady=(0, 10))

        # --- Información del texto ---
        self.text_stats_label = tk.Label(scrollable_frame, text="📊 Estadísticas: No hay texto cargado", 
                                       font=("Segoe UI", 10, "bold"), fg="#b0b0b0", bg="#1a1a1a")
        self.text_stats_label.pack(pady=5)

        # --- Áreas de tipeo con diseño moderno ---
        typing_container = tk.Frame(scrollable_frame, bg="#1a1a1a")
        typing_container.pack(fill=tk.BOTH, expand=True, pady=(10, 15))

        # Texto a copiar
        copy_frame = tk.Frame(typing_container, bg="#2d2d2d", relief="solid", bd=1)
        copy_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 7))

        copy_header = tk.Frame(copy_frame, bg="#2d2d2d")
        copy_header.pack(fill=tk.X, padx=10, pady=(8, 5))

        copy_title = tk.Label(copy_header, text="📖 Texto de Referencia", 
                             font=("Segoe UI", 8, "bold"), fg="#00d4ff", bg="#2d2d2d")
        copy_title.pack(anchor="w")

        self.display_text_area = scrolledtext.ScrolledText(copy_frame, wrap=tk.WORD, width=50, height=22, 
                                                          font=("Consolas", 13), state=tk.DISABLED,
                                                          bg="#1a1a1a", fg="#e0e0e0",
                                                          relief="flat", bd=10)
        self.display_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Área de tipeo
        type_frame = tk.Frame(typing_container, bg="#2d2d2d", relief="solid", bd=1)
        type_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(7, 5))

        type_header = tk.Frame(type_frame, bg="#2d2d2d")
        type_header.pack(fill=tk.X, padx=10, pady=(8, 5))

        type_title = tk.Label(type_header, text="⌨️ Tu Escritura", 
                             font=("Segoe UI", 8, "bold"), fg="#00d4ff", bg="#2d2d2d")
        type_title.pack(anchor="w")

        error_hint = tk.Label(type_header, text="(Los errores aparecerán en rojo)", 
                             font=("Segoe UI", 9), fg="#ff6b6b", bg="#2d2d2d")
        error_hint.pack(anchor="w")

        self.typing_area = scrolledtext.ScrolledText(type_frame, wrap=tk.WORD, width=50, height=22, 
                                                    font=("Consolas", 13),
                                                    bg="#1a1a1a", fg="#ffffff",
                                                    insertbackground="#00d4ff",
                                                    selectbackground="#0078d4",
                                                    selectforeground="#ffffff",
                                                    relief="flat", bd=10)
        self.typing_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        self.typing_area.bind("<KeyRelease>", self.update_typing_feedback)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        # Configurar tags para colorear
        self.typing_area.tag_configure("error", foreground="#ff6b6b", font=("Consolas", 10, "bold"))
        self.typing_area.tag_configure("correct", foreground="#00ff88", font=("Consolas", 10))

        # --- Botones de control con diseño mejorado ---
        control_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        control_frame.pack(fill=tk.X, pady=10)

        buttons_container = tk.Frame(control_frame, bg="#1a1a1a")
        buttons_container.pack()

        self.start_button = tk.Button(buttons_container, text="🚀 INICIAR PRÁCTICA", 
                                    command=self.start_typing, 
                                    font=("Segoe UI", 8, "bold"), 
                                    bg="#00ff88", fg="#1a1a1a", 
                                    activebackground="#00e577", 
                                    relief="flat", bd=0, cursor="hand2", 
                                    padx=25, pady=12)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(buttons_container, text="🔄 REINICIAR", 
                                    command=self.reset_session, 
                                    font=("Segoe UI", 8, "bold"), 
                                    bg="#ff6b35", fg="white", 
                                    activebackground="#e55a2b", 
                                    relief="flat", bd=0, cursor="hand2", 
                                    padx=25, pady=12)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # --- Panel de estadísticas moderno ---
        stats_frame = tk.Frame(scrollable_frame, bg="#0f0f23", relief="solid", bd=2)
        stats_frame.pack(fill=tk.X, pady=15, padx=5)

        stats_header = tk.Label(stats_frame, text="📊 Estadísticas en Tiempo Real", 
                               font=("Segoe UI", 10, "bold"), fg="#00d4ff", bg="#0f0f23")
        stats_header.pack(pady=(12, 8))

        stats_grid = tk.Frame(stats_frame, bg="#0f0f23")
        stats_grid.pack(pady=(0, 15))

        # Crear cajas de estadísticas individuales
        stat_boxes = tk.Frame(stats_grid, bg="#0f0f23")
        stat_boxes.pack()

        # Timer
        timer_box = tk.Frame(stat_boxes, bg="#1a1a2e", relief="raised", bd=2)
        timer_box.pack(side=tk.LEFT, padx=8, pady=5)
        self.timer_label = tk.Label(timer_box, text="⏱️ Tiempo\n00:00", 
                                   font=("Segoe UI", 8, "bold"), 
                                   fg="#ffffff", bg="#1a1a2e", padx=15, pady=10)
        self.timer_label.pack()

        # WPM
        wpm_box = tk.Frame(stat_boxes, bg="#1a1a2e", relief="raised", bd=2)
        wpm_box.pack(side=tk.LEFT, padx=8, pady=5)
        self.wpm_label = tk.Label(wpm_box, text="⚡ Velocidad\n0 WPM", 
                                 font=("Segoe UI", 8, "bold"), 
                                 fg="#00ff88", bg="#1a1a2e", padx=15, pady=10)
        self.wpm_label.pack()

        # Target WPM
        target_box = tk.Frame(stat_boxes, bg="#1a1a2e", relief="raised", bd=2)
        target_box.pack(side=tk.LEFT, padx=8, pady=5)
        self.target_wpm_label = tk.Label(target_box, text="🎯 Objetivo\n0 WPM", 
                                       font=("Segoe UI", 8, "bold"), 
                                       fg="#ffaa00", bg="#1a1a2e", padx=15, pady=10)
        self.target_wpm_label.pack()

        # Correct Words
        words_box = tk.Frame(stat_boxes, bg="#1a1a2e", relief="raised", bd=2)
        words_box.pack(side=tk.LEFT, padx=8, pady=5)
        self.correct_words_label = tk.Label(words_box, text="✅ Correctas\n0", 
                                          font=("Segoe UI", 8, "bold"), 
                                          fg="#00d4ff", bg="#1a1a2e", padx=15, pady=10)
        self.correct_words_label.pack()

    def update_time_selection(self):
        """Actualiza la selección de tiempo"""
        selected = self.time_var.get()
        if selected == 0:  # Personalizado
            self.custom_time_button.config(state=tk.NORMAL)
            self.selected_time_label.config(text="Tiempo seleccionado: Personalizado")
        else:
            self.custom_time_button.config(state=tk.DISABLED)
            self.selected_time = selected
            self.max_time_seconds = selected * 60
            self.selected_time_label.config(text=f"Tiempo seleccionado: {selected} minuto{'s' if selected != 1 else ''}")
            self.update_target_wpm()

    def set_custom_time(self):
        """Permite al usuario establecer un tiempo personalizado"""
        custom_time = simpledialog.askinteger("Tiempo Personalizado", 
                                            "Ingresa el tiempo en minutos (1-60):", 
                                            minvalue=1, maxvalue=60)
        if custom_time:
            self.selected_time = custom_time
            self.max_time_seconds = custom_time * 60
            self.selected_time_label.config(text=f"Tiempo seleccionado: {custom_time} minuto{'s' if custom_time != 1 else ''}")
            self.update_target_wpm()

    def update_target_wpm(self):
        """Actualiza el WPM objetivo basado en el texto y tiempo seleccionado"""
        if self.word_count > 0 and self.selected_time > 0:
            self.target_wpm = self.word_count / self.selected_time
            self.target_wpm_label.config(text=f"🎯 Objetivo\n{self.target_wpm:.1f} WPM")
        else:
            self.target_wpm_label.config(text="🎯 Objetivo\n0 WPM")

    def clean_text(self, text):
        return text.strip()

    def get_words_from_text(self, text):
        return re.findall(r'\b\w+\b', text, re.UNICODE)

    def load_text(self):
        self.source_text = self.paste_text_area.get("1.0", tk.END).strip()
        if not self.source_text:
            messagebox.showwarning("Advertencia", "Por favor, pega el texto en el área de carga.")
            return

        self.source_text = self.clean_text(self.source_text)
        self.source_words = self.get_words_from_text(self.source_text)
        self.word_count = len(self.source_words)

        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.insert("1.0", self.source_text)
        self.display_text_area.config(state=tk.DISABLED)

        # Actualizar estadísticas del texto
        char_count = len(self.source_text)
        self.text_stats_label.config(text=f"📊 Estadísticas: {self.word_count} palabras • {char_count} caracteres")
        
        # Actualizar WPM objetivo
        self.update_target_wpm()

        self.typing_area.config(state=tk.DISABLED)
        self.timer_label.config(text="⏱️ Tiempo\n00:00")
        self.wpm_label.config(text="⚡ Velocidad\n0 WPM")
        self.correct_words_label.config(text="✅ Correctas\n0")
        self.start_button.config(state=tk.NORMAL)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        messagebox.showinfo("✅ Texto Cargado", 
                          f"¡Perfecto! Texto cargado exitosamente.\n\n"
                          f"📝 Palabras: {self.word_count}\n"
                          f"🎯 WPM Objetivo: {self.target_wpm:.1f}\n\n"
                          f"¡Ya puedes iniciar la práctica!")

    def start_typing(self):
        if not self.source_text:
            messagebox.showwarning("⚠️ Texto Requerido", "Primero debes cargar un texto para practicar.")
            return

        if self.timer_running:
            return

        self.typing_area.config(state=tk.NORMAL)
        self.typing_area.focus_set()
        self.start_button.config(state=tk.DISABLED)

        messagebox.showinfo("🚀 ¡Comenzemos!", 
                          "¡Perfecto! El cronómetro iniciará con tu primera pulsación.\n\n"
                          "💡 Consejo: Mantén la calma y concéntrate en la precisión.")

    def start_timer_on_first_key(self, event=None):
        if not self.timer_running and self.source_text:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()
            self.typing_area.unbind("<KeyPress>")

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"⏱️ Tiempo\n{minutes:02}:{seconds:02}")

            # Actualizar WPM en tiempo real
            self.update_real_time_wpm()

            if elapsed_time >= self.max_time_seconds:
                self.finish_typing()
                messagebox.showinfo("⏰ ¡Tiempo Agotado!", 
                                  "¡Se acabó el tiempo! Veamos qué tal lo hiciste.")
            else:
                self.master.after(1000, self.update_timer)

    def update_real_time_wpm(self):
        """Actualiza el WPM en tiempo real mientras se tipea"""
        if not self.timer_running or not self.start_time:
            return

        elapsed_time = time.time() - self.start_time
        if elapsed_time < 1:
            return

        typed_text = self.typing_area.get("1.0", "end-1c")
        typed_words = self.get_words_from_text(typed_text)

        correct_words_count = 0
        for i, source_word in enumerate(self.source_words):
            if i < len(typed_words) and source_word == typed_words[i]:
                correct_words_count += 1

        wpm = (correct_words_count / (elapsed_time / 60)) if elapsed_time > 0 else 0
        self.wpm_label.config(text=f"⚡ Velocidad\n{wpm:.1f} WPM")
        self.correct_words_label.config(text=f"✅ Correctas\n{correct_words_count}")

    def update_typing_feedback(self, event=None):
        typed_text = self.typing_area.get("1.0", "end-1c")
        self.typing_area.delete("1.0", tk.END)

        if not self.source_text:
            return

        compare_length = min(len(typed_text), len(self.source_text))

        for i in range(compare_length):
            source_char = self.source_text[i]
            typed_char = typed_text[i]

            if source_char == typed_char:
                self.typing_area.insert(tk.END, typed_char, "correct")
            else:
                self.typing_area.insert(tk.END, typed_char, "error")

        if len(typed_text) > compare_length:
            self.typing_area.insert(tk.END, typed_text[compare_length:])

        if typed_text == self.source_text:
            self.finish_typing()
            messagebox.showinfo("🎉 ¡Increíble!", 
                              f"¡Felicitaciones! Completaste todo el texto.\n\n"
                              f"⏱️ Tiempo: {self.get_elapsed_time_string()}\n"
                              f"🏆 ¡Eres genial!")

    def get_elapsed_time_string(self):
        """Retorna el tiempo transcurrido en formato legible"""
        if not self.start_time:
            return "0:00"
        
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        return f"{minutes}:{seconds:02d}"

    def finish_typing(self):
        if not self.timer_running:
            return

        self.timer_running = False
        self.typing_area.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        elapsed_time = time.time() - self.start_time if self.start_time else 0
        typed_text = self.typing_area.get("1.0", "end-1c")
        typed_words = self.get_words_from_text(typed_text)

        correct_words_count = 0
        for i, source_word in enumerate(self.source_words):
            if i < len(typed_words) and source_word == typed_words[i]:
                correct_words_count += 1

        wpm = (correct_words_count / (elapsed_time / 60)) if elapsed_time > 0 else 0

        self.wpm_label.config(text=f"⚡ Final\n{wpm:.1f} WPM")
        self.correct_words_label.config(text=f"✅ Correctas\n{correct_words_count}/{len(self.source_words)}")

        accuracy = (correct_words_count / len(self.source_words)) * 100 if len(self.source_words) > 0 else 0
        target_achieved = "¡SÍ! 🎉" if wpm >= self.target_wpm else "Casi... 💪"
        
        # Determinar nivel de rendimiento
        if accuracy >= 95 and wpm >= self.target_wpm:
            performance = "🏆 ¡EXCELENTE!"
        elif accuracy >= 90 and wpm >= self.target_wpm * 0.8:
            performance = "🥈 ¡MUY BIEN!"
        elif accuracy >= 80:
            performance = "🥉 ¡BIEN!"
        else:
            performance = "💪 ¡SIGUE PRACTICANDO!"
        
        messagebox.showinfo("📊 Resultados Finales", 
                          f"{performance}\n\n"
                          f"⏱️ Tiempo Total: {self.get_elapsed_time_string()}\n"
                          f"⚡ Velocidad Final: {wpm:.1f} WPM\n"
                          f"🎯 Objetivo: {self.target_wpm:.1f} WPM\n"
                          f"✅ ¿Objetivo Alcanzado?: {target_achieved}\n"
                          f"📝 Palabras Correctas: {correct_words_count}/{len(self.source_words)}\n"
                          f"🎯 Precisión: {accuracy:.1f}%\n\n"
                          f"¡Sigue practicando para mejorar!")

    def reset_session(self):
        # Detener el temporizador si está corriendo
        self.timer_running = False
        
        # Limpiar variables de estado
        self.source_text = ""
        self.source_words = []
        self.word_count = 0
        self.start_time = None

        # Limpiar y habilitar el área de tipeo
        self.typing_area.config(state=tk.NORMAL)
        self.typing_area.delete("1.0", tk.END)
        self.typing_area.config(state=tk.DISABLED)
        
        # Limpiar área de texto pegado
        self.paste_text_area.delete("1.0", tk.END)
        
        # Limpiar área de texto a copiar
        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.DISABLED)

        # Restaurar etiquetas de estadísticas
        self.timer_label.config(text="⏱️ Tiempo\n00:00")
        self.wpm_label.config(text="⚡ Velocidad\n0 WPM")
        self.target_wpm_label.config(text="🎯 Objetivo\n0 WPM")
        self.correct_words_label.config(text="✅ Correctas\n0")
        self.text_stats_label.config(text="📊 Estadísticas: No hay texto cargado")

        # Restaurar botones
        self.start_button.config(state=tk.NORMAL)
        
        # Volver a enlazar el evento KeyPress para el área de tipeo
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTutorApp(root)
    root.mainloop()