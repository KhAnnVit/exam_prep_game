import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

FILE_NAME = 'exam_questions.csv'


class ExamGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Экзаменационный Квест: Философия")
        self.root.geometry("950x800")
        self.root.configure(bg="#f0f2f5")

        self.df = None
        self.current_q_index = None

        self.init_data()
        self.create_widgets()
        self.load_random_question()

    def init_data(self):
        """Загружает CSV файл"""
        if not os.path.exists(FILE_NAME):
            messagebox.showerror("Ошибка", f"Файл '{FILE_NAME}' не найден!")
            self.root.quit()
            return
        self.df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')

    def save_data(self):
        """Сохраняет текущее состояние в CSV"""
        self.df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')

    def create_widgets(self):
        """Создает интерфейс с вкладками"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", font=("Segoe UI", 12, "bold"), padding=[20, 10])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        # --- Вкладка 1: ИГРА ---
        self.game_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.game_frame, text="🎮 Игра")

        self.lbl_q_number = tk.Label(self.game_frame, text="Вопрос #", font=("Segoe UI", 14, "bold"), fg="#555")
        self.lbl_q_number.pack(pady=10)

        self.lbl_question = tk.Label(self.game_frame, text="", font=("Segoe UI", 16), wraplength=800, justify="center")
        self.lbl_question.pack(pady=20)

        self.btn_show_answer = ttk.Button(self.game_frame, text="👀 Показать ответ", command=self.show_answer)
        self.btn_show_answer.pack(pady=10)

        # ScrolledText для длинных ответов
        self.txt_answer = ScrolledText(
            self.game_frame,
            font=("Segoe UI", 12),
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED,
            bg="#e8f4f8",
            fg="#333"
        )

        tk.Label(self.game_frame, text="Оцени свой ответ:", font=("Segoe UI", 12, "bold")).pack(pady=20)

        # Кнопки оценки РАЗНЫХ ЦВЕТОВ
        self.score_frame = tk.Frame(self.game_frame)
        self.score_frame.pack(pady=10)

        # Цвета: 0-2 красные, 3 желтая, 4-5 зеленые
        colors = ["#ff4d4d", "#ff6666", "#ff8080", "#ffd700", "#90ee90", "#4caf50"]

        for i in range(6):
            btn = tk.Button(
                self.score_frame,
                text=str(i),
                width=5,
                height=2,
                font=("Segoe UI", 14, "bold"),
                bg=colors[i],
                fg="white",
                activebackground=colors[i],
                activeforeground="white",
                relief=tk.RAISED,
                bd=3,
                command=lambda x=i: self.rate_answer(x)
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.btn_end = ttk.Button(self.game_frame, text="🏁 Завершить игру", command=self.root.quit)
        self.btn_end.pack(pady=30)

        # --- Вкладка 2: СТАТИСТИКА ---
        self.stats_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.stats_frame, text="📊 Статистика")

        self.stats_container = tk.Frame(self.stats_frame, bg="#f0f2f5")
        self.stats_container.pack(fill=tk.BOTH, expand=True)

    def on_tab_change(self, event):
        """Обновляет статистику при переключении на вкладку"""
        if self.notebook.tab(self.notebook.select(), "text") == "📊 Статистика":
            self.update_stats()

    def load_random_question(self):
        """Загружает случайный вопрос с оценкой < 5"""
        available = self.df[self.df['Score'] < 5].copy()

        if available.empty:
            self.lbl_q_number.config(text="🎉 ПОЗДРАВЛЯЕМ!")
            self.lbl_question.config(text="Ты получила оценку 5 по всем 46 вопросам!\nТы готова к экзамену на 100%!")
            self.btn_show_answer.pack_forget()
            self.txt_answer.pack_forget()
            self.score_frame.pack_forget()
            return

        sample = available.sample(n=1).iloc[0]
        self.current_q_index = sample.name

        self.lbl_q_number.config(text=f"Вопрос #{sample['Number']} (Осталось выучить: {len(available)})")
        self.lbl_question.config(text=sample['Question'])

        # Скрываем ответ и сбрасываем текст
        self.txt_answer.pack_forget()
        self.txt_answer.config(state=tk.NORMAL)
        self.txt_answer.delete('1.0', tk.END)
        self.txt_answer.insert(tk.END, sample['Answer'])
        self.txt_answer.config(state=tk.DISABLED)

        self.btn_show_answer.config(state=tk.NORMAL)

    def show_answer(self):
        """Показывает текст ответа с прокруткой"""
        self.txt_answer.pack(pady=20, fill=tk.BOTH, expand=True)
        self.btn_show_answer.config(state=tk.DISABLED)

    def rate_answer(self, score):
        """Сохраняет оценку и загружает следующий вопрос"""
        if self.current_q_index is not None:
            self.df.at[self.current_q_index, 'Score'] = score
            self.save_data()

        self.load_random_question()

    def update_stats(self):
        """Отрисовывает Heatmap и Pie Chart"""
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        self.df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')

        # Создаем фигуру с двумя подграфиками
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.patch.set_facecolor('#f0f2f5')

        # 1. Heatmap (горизонтальный)
        scores_matrix = [self.df['Score'].tolist()]

        sns.heatmap(scores_matrix, annot=False, cmap="RdYlGn", vmin=0, vmax=5,
                    cbar=True, ax=ax1, linewidths=1, linecolor='white')

        ax1.set_title("Прогресс по каждому вопросу (0 = красный, 5 = зеленый)",
                      fontsize=14, fontweight='bold', pad=20)
        ax1.set_xlabel("Номер вопроса", fontsize=12, labelpad=10)
        ax1.set_xticks(range(0, 46, 5))
        ax1.set_xticklabels([str(i + 1) for i in range(0, 46, 5)], rotation=0)

        # 2. Pie Chart
        counts = self.df['Score'].value_counts().reindex(range(6), fill_value=0)
        colors = ['#ff4d4d', '#ff6666', '#ff8080', '#ffd700', '#90ee90', '#4caf50']

        non_zero_mask = counts > 0
        if non_zero_mask.any():
            filtered_counts = counts[non_zero_mask]
            filtered_labels = [f"Оценка {i}: {counts[i]} шт." for i in range(6) if counts[i] > 0]
            filtered_colors = [colors[i] for i in range(6) if counts[i] > 0]

            ax2.pie(filtered_counts,
                    labels=filtered_labels,
                    colors=filtered_colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops={'fontsize': 11},
                    pctdistance=0.45)
        else:
            ax2.text(0.5, 0.5, 'Начни игру, чтобы увидеть прогресс!',
                     ha='center', va='center', fontsize=14, transform=ax2.transAxes)

        ax2.set_title("Распределение оценок", fontsize=14, fontweight='bold', pad=20)
        ax2.axis('equal')

        # Настраиваем отступы между графиками
        plt.tight_layout(pad=3.0, h_pad=5.0)

        canvas = FigureCanvasTkAgg(fig, master=self.stats_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamGameApp(root)
    root.mainloop()