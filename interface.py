from tkinter import Tk, Frame, BOTH
 
class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        self.create_menu()
    
    def create_menu(self):
        self.pack(fill=BOTH, expand=1)
         
if __name__ == '__main__':
    root = Tk()
    root.title("Пример 1. Курс 'Создание графического редактора на python'")
    root.geometry("650x650+100+100")
    app = Example(root)
    root.mainloop()