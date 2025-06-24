import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, messagebox, filedialog
import logging
import os
import shutil
from datetime import datetime
from log_filters import WarningLogFilter


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


EMPLOYEES = [
    "Галимзянова",
    "Мезитова",
    "Буторина",
    "Мухаметова",
    "Нечаева",
    "Романова",
    "Гафиятуллина",
    "Киямова",
    "Романова",
    "Саттарова",
    "Сивелькина"
]


class App(tk.Tk):
    def __init__(self,processor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Авто-Подача МВД")
        self.geometry("700x500")

        ttk.Label(self, text="Сотрудник:").pack(anchor="w", padx=10, pady=(10,0))
        self.cmb_employee = ttk.Combobox(self, values=EMPLOYEES, state="readonly")
        self.cmb_employee.pack(fill="x", padx=10)

        # 2) Тип заявки
        ttk.Label(self, text="Тип подачи:").pack(anchor="w", padx=10, pady=(10,0))
        self.loan_type_var = tk.StringVar()
        self.cmb_type = ttk.Combobox(
            self,
            textvariable=self.loan_type_var,
            values=["ПС", "ДК"],
            state="readonly"
        )
        self.cmb_type.pack(fill="x", padx=10)
        # Установим первый элемент ("ps") как текущий
        self.cmb_type.current(0)

        ttk.Button(self, text="Выбрать папку…", command=self.on_browse).pack(fill="x", padx=10, pady=(10,0))
        self.root_folder_var = tk.StringVar(value="— не выбрано —")
        ttk.Label(self, textvariable=self.root_folder_var).pack(fill="x", padx=10)

        self.btn_start    = tk.Button(self, text="Запустить",   command=self.on_start)
        self.btn_continue = tk.Button(self, text="Продолжить",  command=self.on_continue, state="disabled")
        self.btn_exit     = tk.Button(self, text="Выход",       command=self.on_exit)
        self.btn_next = tk.Button(self, text="Пропустить договор",   command=self.on_next, state="disabled")
        for b in (self.btn_start, self.btn_continue, self.btn_exit, self.btn_next):
            b.pack(side="left", expand=True, padx=5)

        # Поле для логов (с полосой прокрутки)
        self.log_widget = ScrolledText(self, state="disabled", height=20)
        self.log_widget.pack(side="bottom", fill="both", expand=True)

        # Настраиваем логирование: все вызовы logger.info/etc пойдут в это поле
        handler = TkLoggerHandler(self.log_widget)
        handler.setLevel(logging.WARNING)
        handler.addFilter(WarningLogFilter())
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        # События для управления паузой/останoвом в оркестраторе
        self._pause_event = threading.Event()
        self._stop_event  = threading.Event()
        self._skip_event  = threading.Event()

        # Экземпляр вашего LoanProcessor
        self.processor = processor
        self.processor._on_pause = self.show_pause_prompt
        self.processor._skip_event = self.on_next



    def on_browse(self):
        fld = filedialog.askdirectory(initialdir="\\\\Pczaitenov\\159\\Ежедневная подача")
        if fld:
            self.root_folder_var.set(fld)


    def show_pause_prompt(self, prompt: str):
        """ Отобразить в логах GUI текст prompt и активировать кнопку Continue """
        # вставляем текст в ScrolledText
        self.log_widget.configure(state="normal")
        self.log_widget.insert(tk.END, prompt + "\n")
        self.log_widget.configure(state="disabled")
        # разблокируем кнопку Continue
        self.btn_continue.configure(state="normal")
        self.btn_next.configure(state="normal")   # <- вот тут


    def on_start(self):

        employee  = self.cmb_employee.get()
        loan_type = self.loan_type_var.get()
        source_dir = self.root_folder_var.get()
        if not employee or loan_type not in ("ПС", "ДК") or source_dir == "— не выбрано —":
            messagebox.showerror("Ошибка", "Выберите сотрудника, тип заявки и папку для обработки.")
            return

        # строим пути и создаём папки
        base = r"\\Pczaitenov\159\Ежедневная подача"
        emp_dir = os.path.join(base, employee)
        os.makedirs(emp_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(emp_dir, today)
        os.makedirs(date_dir, exist_ok=True)

        for name in os.listdir(source_dir):
            src_path = os.path.join(source_dir, name)
            dst_path = os.path.join(date_dir, name)
            # Перемещаем только папки (если нужно — можно и файлы)
            if os.path.isdir(src_path):
                try:
                    shutil.move(src_path, dst_path)
                    logging.info(f"Перемещено: {name}")
                except Exception as e:
                    logging.warning(f"Не удалось переместить {name}: {e}")

        if not any(os.path.isdir(os.path.join(date_dir, d)) for d in os.listdir(date_dir)):
            messagebox.showwarning("Внимание", "В выбранной папке не было папок для обработки.")
            return
        
        success_dir = os.path.join(emp_dir, "processed")
        failed_dir  = os.path.join(emp_dir, "failed")
        os.makedirs(success_dir, exist_ok=True)
        os.makedirs(failed_dir,  exist_ok=True)

        # передаём всё в процессор
        self.processor.root_folder        = date_dir
        self.processor.dst_root           = success_dir
        self.processor.unfulfilled_root   = failed_dir
        self.processor.bd                 = loan_type
        self.processor._skip_event      = self._skip_event
        # сбрасываем флаги и меняем кнопки
        self._pause_event.clear()
        self._stop_event.clear()
        self._skip_event.clear()
        self.btn_start.configure(state="disabled")
        self.btn_continue.configure(state="normal")
        self.btn_next.configure(state="normal")

            
        def target():
            try:
                logging.info(">>> Запускаю LoanProcessor.run()")
                self.processor.run(
                    pause_event=self._pause_event,
                    stop_event =self._stop_event,
                    skip_event  =self._skip_event
                )
                logging.info("<<< LoanProcessor.run() завершён")
            except Exception:
                logging.exception("Ошибка внутри processor.run()")
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def on_continue(self):
        # поднимаем событие, процессор выйдет из _pause()
        self.processor._wait_for_continue.set()
        self.btn_continue.configure(state="disabled")

    def on_exit(self):
        # Сигналим потоку, что пора остановиться
        self._stop_event.set()
        # Дополнительно сразу же пытаемся убить браузер
        try:
            if hasattr(self.processor, "driver"):
                self.processor.driver.quit()
        except Exception:
            pass
        # Закрываем GUI
        self.destroy()

    def on_next(self):
        self._skip_event.set()
        self.btn_next.configure(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()