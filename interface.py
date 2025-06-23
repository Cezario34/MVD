import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging

from orchestrator import LoanProcessor  # или как у вас называется ветка с .run()

class TkLoggerHandler(logging.Handler):
    """Переадресует записи из logging в Text-виджет."""
    def __init__(self, text_widget: ScrolledText):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record) + "\n"
        # Убедимся, что можем писать в текст
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg)
        self.text_widget.configure(state="disabled")
        # Прокрутка вниз
        self.text_widget.yview(tk.END)

class App(tk.Tk):
    def __init__(self,processor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Авто-Подача МВД")
        self.geometry("700x500")

        # Кнопки
        self.btn_start    = tk.Button(self, text="Запустить",   command=self.on_start)
        self.btn_continue = tk.Button(self, text="Продолжить",  command=self.on_continue, state="disabled")
        self.btn_exit     = tk.Button(self, text="Выход",       command=self.on_exit)

        self.btn_start.pack(side="top",   fill="x")
        self.btn_continue.pack(side="top", fill="x")
        self.btn_exit.pack(side="top",    fill="x")

        # Поле для логов (с полосой прокрутки)
        self.log_widget = ScrolledText(self, state="disabled", height=20)
        self.log_widget.pack(side="bottom", fill="both", expand=True)

        # Настраиваем логирование: все вызовы logger.info/etc пойдут в это поле
        handler = TkLoggerHandler(self.log_widget)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        # События для управления паузой/останoвом в оркестраторе
        self._pause_event = threading.Event()
        self._stop_event  = threading.Event()

        # Экземпляр вашего LoanProcessor
        self.processor = processor
        self.processor._on_pause = self.show_pause_prompt

    def show_pause_prompt(self, prompt: str):
        """ Отобразить в логах GUI текст prompt и активировать кнопку Continue """
        # вставляем текст в ScrolledText
        self.log_widget.configure(state="normal")
        self.log_widget.insert(tk.END, prompt + "\n")
        self.log_widget.configure(state="disabled")
        # разблокируем кнопку Continue
        self.btn_continue.configure(state="normal")



    def on_start(self):
        """Запускаем ваш процесс в отдельном потоке, включаем кнопку 'Продолжить'."""
        self.btn_start.configure(state="disabled")
        self.btn_continue.configure(state="normal")
        self._pause_event.clear()
        self._stop_event.clear()

        def target():
            # В вашем LoanProcessor.run() придётся где-то проверять эти эвенты:
            #   if self._stop_event.is_set(): break
            #   self._pause_event.wait()  # когда надо сделать паузу
            self.processor.run(
                pause_event=self._pause_event,
                stop_event =self._stop_event
            )
        threading.Thread(target=target, daemon=True).start()

    def on_continue(self):
        # поднимаем событие, процессор выйдет из _pause()
        self.processor._wait_for_continue.set()
        self.btn_continue.configure(state="disabled")

    def on_exit(self):
        # ставим флаг остановки и «отпускаем» pause, чтобы цикл завершился
        self.processor._should_stop = True
        self.processor._wait_for_continue.set()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()