import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import time
import re

class TypingTutorApp:
    def __init__(self, master):
        self.master = master
        master.title("Entrenador de Tipeo")
        master.geometry("1200x800") # Aumenté altura
        master.configure(bg="#f0f0f0")

        self.source_text = ""
        self.start_time = None
        self.timer_running = False
        self.max_time_seconds = 4 * 60 # Por defecto 4 minutos
        self.selected_time = 4 # Tiempo seleccionado en minutos
        self.word_count = 0 # Contador de palabras del texto
        self.target_wpm = 0 # WPM objetivo para completar en el tiempo establecido

        self.create_widgets()
        self.reset_session()

    def create_widgets(self):
        # --- Frame Principal con scroll ---
        canvas = tk.Canvas(self.master, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(self.master, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # --- Título ---
        title_label = tk.Label(scrollable_frame, text="¡Mejora tu Velocidad de Tipeo!", 
                              font=("Inter", 24, "bold"), fg="#333", bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # --- Configuración de Tiempo ---
        time_config_frame = tk.LabelFrame(scrollable_frame, text="Configuración de Tiempo", 
                                         font=("Inter", 12, "bold"), bg="#fff", fg="#555", 
                                         bd=2, relief="groove", padx=15, pady=15)
        time_config_frame.pack(fill=tk.X, pady=(0, 15))

        self.time_var = tk.IntVar(value=4)
        
        time_buttons_frame = tk.Frame(time_config_frame, bg="#fff")
        time_buttons_frame.pack(pady=5)

        tk.Radiobutton(time_buttons_frame, text="1 minuto", variable=self.time_var, value=1, 
                      command=self.update_time_selection, font=("Inter", 11), bg="#fff").pack(side=tk.LEFT, padx=15)
        
        tk.Radiobutton(time_buttons_frame, text="4 minutos", variable=self.time_var, value=4, 
                      command=self.update_time_selection, font=("Inter", 11), bg="#fff").pack(side=tk.LEFT, padx=15)
        
        tk.Radiobutton(time_buttons_frame, text="Personalizado", variable=self.time_var, value=0, 
                      command=self.update_time_selection, font=("Inter", 11), bg="#fff").pack(side=tk.LEFT, padx=15)
        
        self.custom_time_button = tk.Button(time_buttons_frame, text="Establecer Tiempo", 
                                          command=self.set_custom_time, font=("Inter", 10), 
                                          bg="#17a2b8", fg="white", activebackground="#138496", 
                                          relief="raised", bd=2, cursor="hand2", state=tk.DISABLED)
        self.custom_time_button.pack(side=tk.LEFT, padx=15)

        self.selected_time_label = tk.Label(time_config_frame, text="Tiempo seleccionado: 4 minutos", 
                                          font=("Inter", 11, "bold"), fg="#007BFF", bg="#fff")
        self.selected_time_label.pack(pady=10)

        # --- Área para pegar texto ---
        paste_frame = tk.LabelFrame(scrollable_frame, text="Pega tu texto aquí", 
                                   font=("Inter", 12, "bold"), bg="#fff", fg="#555", 
                                   bd=2, relief="groove", padx=15, pady=15)
        paste_frame.pack(fill=tk.X, pady=(0, 15))

        self.paste_text_area = scrolledtext.ScrolledText(paste_frame, wrap=tk.WORD, width=80, height=5, 
                                                        font=("Inter", 12), bd=1, relief="solid")
        self.paste_text_area.pack(fill=tk.X, pady=(0, 10))

        load_button = tk.Button(paste_frame, text="Cargar Texto para Practicar", command=self.load_text, 
                               font=("Inter", 12, "bold"), bg="#4CAF50", fg="white", 
                               activebackground="#45a049", relief="raised", bd=2, cursor="hand2")
        load_button.pack()

        # --- Información del texto ---
        self.text_stats_label = tk.Label(scrollable_frame, text="Estadísticas del texto: No hay texto cargado", 
                                       font=("Inter", 12, "bold"), fg="#555", bg="#f0f0f0")
        self.text_stats_label.pack(pady=10)

        # --- Áreas de tipeo ---
        typing_container = tk.Frame(scrollable_frame, bg="#f0f0f0")
        typing_container.pack(fill=tk.X, pady=(0, 20))

        # Texto a copiar
        copy_frame = tk.LabelFrame(typing_container, text="Texto a Copiar", 
                                  font=("Inter", 12, "bold"), bg="#fff", fg="#555", 
                                  bd=2, relief="groove", padx=10, pady=10)
        copy_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.display_text_area = scrolledtext.ScrolledText(copy_frame, wrap=tk.WORD, width=40, height=10, 
                                                          font=("Inter", 14), state=tk.DISABLED, bd=1, 
                                                          relief="solid", bg="#e8e8e8", fg="#333")
        self.display_text_area.pack(fill=tk.BOTH, expand=True)

        # Área de tipeo
        type_feedback_frame = tk.LabelFrame(typing_container, text="Tu Tipeo (Errores en Rojo)", 
                                           font=("Inter", 12, "bold"), bg="#fff", fg="#555", 
                                           bd=2, relief="groove", padx=10, pady=10)
        type_feedback_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.typing_area = scrolledtext.ScrolledText(type_feedback_frame, wrap=tk.WORD, width=40, height=10, 
                                                    font=("Inter", 14), bd=1, relief="solid")
        self.typing_area.pack(fill=tk.BOTH, expand=True)
        self.typing_area.bind("<KeyRelease>", self.update_typing_feedback)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        # Configurar tags para colorear
        self.typing_area.tag_configure("error", foreground="red")
        self.typing_area.tag_configure("correct", foreground="green")

        # --- BOTONES DE CONTROL - SECCIÓN SEPARADA ---
        control_section = tk.Frame(scrollable_frame, bg="#f0f0f0", relief="solid", bd=2)
        control_section.pack(fill=tk.X, pady=20, padx=20)

        control_title = tk.Label(control_section, text="CONTROLES", font=("Inter", 14, "bold"), 
                                fg="#333", bg="#f0f0f0")
        control_title.pack(pady=10)

        buttons_frame = tk.Frame(control_section, bg="#f0f0f0")
        buttons_frame.pack(pady=15)

        self.start_button = tk.Button(buttons_frame, text="🚀 INICIAR PRÁCTICA", command=self.start_typing, 
                                    font=("Inter", 16, "bold"), bg="#007BFF", fg="white", 
                                    activebackground="#0056b3", relief="raised", bd=3, cursor="hand2", 
                                    padx=30, pady=15)
        self.start_button.pack(side=tk.LEFT, padx=20)

        self.reset_button = tk.Button(buttons_frame, text="🔄 REINICIAR", command=self.reset_session, 
                                    font=("Inter", 16, "bold"), bg="#DC3545", fg="white", 
                                    activebackground="#c82333", relief="raised", bd=3, cursor="hand2", 
                                    padx=30, pady=15)
        self.reset_button.pack(side=tk.LEFT, padx=20)

        # --- ESTADÍSTICAS EN TIEMPO REAL ---
        stats_section = tk.Frame(scrollable_frame, bg="#f0f0f0", relief="solid", bd=2)
        stats_section.pack(fill=tk.X, pady=(0, 20), padx=20)

        stats_title = tk.Label(stats_section, text="ESTADÍSTICAS", font=("Inter", 14, "bold"), 
                              fg="#333", bg="#f0f0f0")
        stats_title.pack(pady=10)

        stats_grid = tk.Frame(stats_section, bg="#f0f0f0")
        stats_grid.pack(pady=15)

        # Columna izquierda
        left_stats = tk.Frame(stats_grid, bg="#f0f0f0")
        left_stats.pack(side=tk.LEFT, padx=30)

        self.timer_label = tk.Label(left_stats, text="⏱️ Tiempo: 00:00", font=("Inter", 14, "bold"), 
                                   fg="#333", bg="#f0f0f0")
        self.timer_label.pack(pady=5)

        self.wpm_label = tk.Label(left_stats, text="⚡ Velocidad: 0 WPM", font=("Inter", 14, "bold"), 
                                 fg="#333", bg="#f0f0f0")
        self.wpm_label.pack(pady=5)

        # Columna derecha
        right_stats = tk.Frame(stats_grid, bg="#f0f0f0")
        right_stats.pack(side=tk.RIGHT, padx=30)

        self.target_wpm_label = tk.Label(right_stats, text="🎯 WPM Objetivo: 0", font=("Inter", 14, "bold"), 
                                       fg="#28a745", bg="#f0f0f0")
        self.target_wpm_label.pack(pady=5)

        self.correct_words_label = tk.Label(right_stats, text="✅ Palabras Correctas: 0", 
                                          font=("Inter", 14, "bold"), fg="#333", bg="#f0f0f0")
        self.correct_words_label.pack(pady=5)

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
            self.target_wmp_label.config(text=f"🎯 WPM Objetivo: {self.target_wpm:.1f}")
        else:
            self.target_wpm_label.config(text="🎯 WPM Objetivo: 0")

    def clean_text(self, text):
        return text.strip()

    def get_words_from_text(self, text):
        return re.findall(r'\b[a-zA-Z0-9]+\b', text)

    def load_text(self):
        self.source_text = self.paste_text_area.get("1.0", tk.END).strip()
        if not self.source_text:
            messagebox.showwarning("Advertencia", "Por favor, pega el texto en el área de 'Pega tu texto aquí'.")
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
        self.text_stats_label.config(text=f"📊 Estadísticas: {self.word_count} palabras, {char_count} caracteres")
        
        # Actualizar WPM objetivo
        self.update_target_wpm()

        self.typing_area.config(state=tk.DISABLED)
        self.timer_label.config(text="⏱️ Tiempo: 00:00")
        self.wmp_label.config(text="⚡ Velocidad: 0 WPM")
        self.correct_words_label.config(text="✅ Palabras Correctas: 0")
        self.start_button.config(state=tk.NORMAL)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        messagebox.showinfo("✅ Listo", f"Texto cargado con {self.word_count} palabras. ¡Puedes iniciar la práctica!")

    def start_typing(self):
        if not self.source_text:
            messagebox.showwarning("⚠️ Advertencia", "Primero carga un texto para practicar.")
            return

        if self.timer_running:
            return

        self.typing_area.config(state=tk.NORMAL)
        self.typing_area.focus_set()
        self.start_button.config(state=tk.DISABLED)

        messagebox.showinfo("🚀 Inicio", "¡Empieza a tipear! El temporizador se activará con tu primera pulsación.")

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
            self.timer_label.config(text=f"⏱️ Tiempo: {minutes:02}:{seconds:02}")

            # Actualizar WPM en tiempo real
            self.update_real_time_wpm()

            if elapsed_time >= self.max_time_seconds:
                self.finish_typing()
                messagebox.showinfo("⏰ Tiempo Agotado", "¡Se acabó el tiempo! Calculando resultados.")
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
        self.wpm_label.config(text=f"⚡ Velocidad: {wpm:.1f} WPM")
        self.correct_words_label.config(text=f"✅ Palabras Correctas: {correct_words_count}")

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
            messagebox.showinfo("🎉 ¡Completado!", f"¡Felicidades! Has terminado de tipear el texto en {self.get_elapsed_time_string()}!")

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

        self.wpm_label.config(text=f"⚡ Velocidad Final: {wpm:.2f} WPM")
        self.correct_words_label.config(text=f"✅ Palabras Correctas: {correct_words_count}/{len(self.source_words)}")

        accuracy = (correct_words_count / len(self.source_words)) * 100 if len(self.source_words) > 0 else 0
        target_achieved = "¡SÍ!" if wpm >= self.target_wpm else "No"
        
        messagebox.showinfo("📊 Resultados Finales", 
                          f"Sesión completada:\n\n"
                          f"⏱️ Tiempo: {self.get_elapsed_time_string()}\n"
                          f"📊 Velocidad: {wpm:.2f} WPM\n"
                          f"🎯 Objetivo: {self.target_wpm:.1f} WPM\n"
                          f"✅ ¿Objetivo alcanzado?: {target_achieved}\n"
                          f"📝 Palabras correctas: {correct_words_count}/{len(self.source_words)}\n"
                          f"🎯 Precisión: {accuracy:.1f}%")

    def reset_session(self):
        self.source_text = ""
        self.source_words = []
        self.word_count = 0
        self.start_time = None
        self.timer_running = False

        self.paste_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.DISABLED)
        self.typing_area.delete("1.0", tk.END)
        self.typing_area.config(state=tk.DISABLED)

        self.timer_label.config(text="⏱️ Tiempo: 00:00")
        self.wpm_label.config(text="⚡ Velocidad: 0 WPM")
        self.target_wpm_label.config(text="🎯 WPM Objetivo: 0")
        self.correct_words_label.config(text="✅ Palabras Correctas: 0")
        self.text_stats_label.config(text="📊 Estadísticas del texto: No hay texto cargado")

        self.start_button.config(state=tk.NORMAL)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTutorApp(root)
    root.mainloop()