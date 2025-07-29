import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import re

class TypingTutorApp:
    def __init__(self, master):
        self.master = master
        master.title("Entrenador de Tipeo")
        master.geometry("1000x700") # Tamaño inicial de la ventana
        master.configure(bg="#f0f0f0") # Color de fondo

        self.source_text = ""
        self.start_time = None
        self.timer_running = False
        self.max_time_seconds = 4 * 60 # 4 minutos en segundos

        self.create_widgets()
        self.reset_session() # Inicializar la sesión al inicio

    def create_widgets(self):
        # --- Frame Principal ---
        main_frame = tk.Frame(self.master, padx=20, pady=20, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Título ---
        title_label = tk.Label(main_frame, text="¡Mejora tu Velocidad de Tipeo!", font=("Inter", 24, "bold"), fg="#333", bg="#f0f0f0")
        title_label.pack(pady=10)

        # --- Área para pegar texto ---
        paste_frame = tk.LabelFrame(main_frame, text="Pega tu texto aquí", font=("Inter", 12, "bold"), bg="#fff", fg="#555", bd=2, relief="groove", padx=10, pady=10)
        paste_frame.pack(fill=tk.X, pady=10)

        self.paste_text_area = scrolledtext.ScrolledText(paste_frame, wrap=tk.WORD, width=80, height=6, font=("Inter", 12), bd=1, relief="solid")
        self.paste_text_area.pack(fill=tk.BOTH, expand=True)

        load_button = tk.Button(paste_frame, text="Cargar Texto para Practicar", command=self.load_text, font=("Inter", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", relief="raised", bd=2, cursor="hand2")
        load_button.pack(pady=5)

        # --- Contenedor para el texto a copiar y el área de tipeo ---
        typing_container = tk.Frame(main_frame, bg="#f0f0f0")
        typing_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # --- Texto a copiar ---
        copy_frame = tk.LabelFrame(typing_container, text="Texto a Copiar", font=("Inter", 12, "bold"), bg="#fff", fg="#555", bd=2, relief="groove", padx=10, pady=10)
        copy_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.display_text_area = scrolledtext.ScrolledText(copy_frame, wrap=tk.WORD, width=40, height=15, font=("Inter", 14), state=tk.DISABLED, bd=1, relief="solid", bg="#e8e8e8", fg="#333")
        self.display_text_area.pack(fill=tk.BOTH, expand=True)

        # --- Área de tipeo y feedback ---
        type_feedback_frame = tk.LabelFrame(typing_container, text="Tu Tipeo (Errores en Rojo)", font=("Inter", 12, "bold"), bg="#fff", fg="#555", bd=2, relief="groove", padx=10, pady=10)
        type_feedback_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.typing_area = scrolledtext.ScrolledText(type_feedback_frame, wrap=tk.WORD, width=40, height=15, font=("Inter", 14), bd=1, relief="solid")
        self.typing_area.pack(fill=tk.BOTH, expand=True)
        self.typing_area.bind("<KeyRelease>", self.update_typing_feedback)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        # Configurar tags para colorear errores
        self.typing_area.tag_configure("error", foreground="red")
        self.typing_area.tag_configure("correct", foreground="green") # Opcional, para mostrar lo correcto en verde

        # --- Contenedor de Controles y Resultados ---
        controls_results_frame = tk.Frame(main_frame, bg="#f0f0f0")
        controls_results_frame.pack(fill=tk.X, pady=10)

        # Controles
        controls_frame = tk.Frame(controls_results_frame, bg="#f0f0f0")
        controls_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.start_button = tk.Button(controls_frame, text="Iniciar Práctica", command=self.start_typing, font=("Inter", 12, "bold"), bg="#007BFF", fg="white", activebackground="#0056b3", relief="raised", bd=2, cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(controls_frame, text="Reiniciar", command=self.reset_session, font=("Inter", 12, "bold"), bg="#DC3545", fg="white", activebackground="#c82333", relief="raised", bd=2, cursor="hand2")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Resultados
        results_frame = tk.Frame(controls_results_frame, bg="#f0f0f0")
        results_frame.pack(side=tk.RIGHT)

        self.timer_label = tk.Label(results_frame, text="Tiempo: 00:00", font=("Inter", 14, "bold"), fg="#333", bg="#f0f0f0")
        self.timer_label.pack(pady=2)

        self.wpm_label = tk.Label(results_frame, text="Velocidad: 0 WPM", font=("Inter", 14, "bold"), fg="#333", bg="#f0f0f0")
        self.wpm_label.pack(pady=2)

        self.correct_words_label = tk.Label(results_frame, text="Palabras Correctas: 0", font=("Inter", 14, "bold"), fg="#333", bg="#f0f0f0")
        self.correct_words_label.pack(pady=2)

    def clean_text(self, text):
        # Solo elimina los espacios en blanco iniciales y finales.
        # Conserva los espacios internos y los saltos de línea para la comparación.
        return text.strip()

    def get_words_from_text(self, text):
        # Extrae solo palabras (secuencias alfanuméricas) para el conteo de WPM.
        # Esto ignora espacios, saltos de línea y caracteres especiales para el conteo de palabras.
        return re.findall(r'\b[a-zA-Z0-9]+\b', text)

    def load_text(self):
        self.source_text = self.paste_text_area.get("1.0", tk.END).strip()
        if not self.source_text:
            messagebox.showwarning("Advertencia", "Por favor, pega el texto en el área de 'Pega tu texto aquí'.")
            return

        # Aplica clean_text al texto fuente para prepararlo para la visualización y comparación
        self.source_text = self.clean_text(self.source_text)
        # Obtiene las palabras para el cálculo de WPM del texto fuente limpio
        self.source_words = self.get_words_from_text(self.source_text)

        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.insert("1.0", self.source_text)
        self.display_text_area.config(state=tk.DISABLED)

        # Asegurarse de que el área de tipeo esté deshabilitada hasta que se inicie la práctica
        self.typing_area.config(state=tk.DISABLED)
        self.timer_label.config(text="Tiempo: 00:00")
        self.wpm_label.config(text="Velocidad: 0 WPM")
        self.correct_words_label.config(text="Palabras Correctas: 0")
        self.start_button.config(state=tk.NORMAL)
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

        messagebox.showinfo("Listo", "Texto cargado. ¡Puedes iniciar la práctica!")

    def start_typing(self):
        if not self.source_text:
            messagebox.showwarning("Advertencia", "Primero carga un texto para practicar.")
            return

        if self.timer_running:
            return # Ya está corriendo

        self.typing_area.config(state=tk.NORMAL)
        self.typing_area.focus_set() # Pone el foco en el área de tipeo
        self.start_button.config(state=tk.DISABLED) # Deshabilita el botón de inicio

        # El temporizador se inicia con la primera pulsación de tecla
        messagebox.showinfo("Inicio", "¡Empieza a tipear! El temporizador se activará con tu primera pulsación.")

    def start_timer_on_first_key(self, event=None):
        if not self.timer_running and self.source_text:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()
            self.typing_area.unbind("<KeyPress>") # Desvincula para que no se reinicie el timer

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"Tiempo: {minutes:02}:{seconds:02}")

            if elapsed_time >= self.max_time_seconds:
                self.finish_typing()
                messagebox.showinfo("Tiempo Agotado", "¡Se acabó el tiempo! Calculando resultados.")
            else:
                self.master.after(1000, self.update_timer) # Actualiza cada segundo

    def update_typing_feedback(self, event=None):
        # Obtiene el texto tipeado, excluyendo el carácter de nueva línea extra que Tkinter añade
        typed_text = self.typing_area.get("1.0", "end-1c")
        self.typing_area.delete("1.0", tk.END) # Borra todo para reinsertar con tags

        # Asegurarse de que source_text no esté vacío antes de continuar
        if not self.source_text:
            return

        # Limitar la comparación a la longitud del texto más corto para evitar errores de índice
        compare_length = min(len(typed_text), len(self.source_text))

        for i in range(compare_length):
            source_char = self.source_text[i]
            typed_char = typed_text[i]

            if source_char == typed_char:
                self.typing_area.insert(tk.END, typed_char, "correct")
            else:
                self.typing_area.insert(tk.END, typed_char, "error")

        # Insertar el resto del texto tipeado (si el usuario tipeó más que el texto fuente) sin tags
        if len(typed_text) > compare_length:
            self.typing_area.insert(tk.END, typed_text[compare_length:])

        # Si el usuario ha tipeado todo el texto fuente exactamente, finaliza la sesión
        # Esta comparación ahora funciona correctamente porque ambos textos están sin nuevas líneas finales
        if typed_text == self.source_text:
            self.finish_typing()
            messagebox.showinfo("Completado", "¡Has terminado de tipear el texto!")

    def finish_typing(self):
        if not self.timer_running: # Evita calcular dos veces si ya se detuvo
            return

        self.timer_running = False
        self.typing_area.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        elapsed_time = time.time() - self.start_time if self.start_time else 0

        # Obtiene el texto tipeado final, sin la nueva línea final de Tkinter
        typed_text = self.typing_area.get("1.0", "end-1c")
        # Usa get_words_from_text para obtener solo palabras reales del texto tipeado para la comparación
        typed_words = self.get_words_from_text(typed_text)

        correct_words_count = 0
        for i, source_word in enumerate(self.source_words):
            if i < len(typed_words) and source_word == typed_words[i]:
                correct_words_count += 1

        # Calcular WPM: (Palabras correctas / tiempo en minutos)
        wpm = 0
        if elapsed_time > 0:
            wpm = (correct_words_count / (elapsed_time / 60))

        self.wpm_label.config(text=f"Velocidad: {wpm:.2f} WPM")
        self.correct_words_label.config(text=f"Palabras Correctas: {correct_words_count}")

    def reset_session(self):
        self.source_text = ""
        self.source_words = []
        self.start_time = None
        self.timer_running = False

        self.paste_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.DISABLED)
        self.typing_area.delete("1.0", tk.END)
        self.typing_area.config(state=tk.DISABLED) # Deshabilita el área de tipeo hasta cargar texto

        self.timer_label.config(text="Tiempo: 00:00")
        self.wpm_label.config(text="Velocidad: 0 WPM")
        self.correct_words_label.config(text="Palabras Correctas: 0")

        self.start_button.config(state=tk.NORMAL)
        # Volver a vincular el evento KeyPress para iniciar el timer
        self.typing_area.bind("<KeyPress>", self.start_timer_on_first_key)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTutorApp(root)
    root.mainloop()