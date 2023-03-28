import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")
        self.result = 0
        self.current = 0
        self.operator = ""
        self.build_gui()

    def build_gui(self):
        self.display_var = tk.StringVar()
        display = tk.Entry(self.master, textvariable=self.display_var, font=("Arial", 16), bd=5, justify=tk.RIGHT)
        display.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        display.insert(0, "0")

        button_list = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+",
            "C"
        ]

        row_index = 1
        col_index = 0
        for button_text in button_list:
            button = tk.Button(self.master, text=button_text, font=("Arial", 14), width=5, height=2, command=lambda x=button_text: self.button_click(x))
            button.grid(row=row_index, column=col_index, padx=5, pady=5)
            col_index += 1
            if col_index > 3:
                col_index = 0
                row_index += 1

    def button_click(self, button_text):
        if button_text in ["+", "-", "*", "/"]:
            self.operator = button_text
            self.current = float(self.display_var.get())
            self.display_var.set("")
        elif button_text == "=":
            if self.operator == "+":
                self.result = self.current + float(self.display_var.get())
            elif self.operator == "-":
                self.result = self.current - float(self.display_var.get())
            elif self.operator == "*":
                self.result = self.current * float(self.display_var.get())
            elif self.operator == "/":
                self.result = self.current / float(self.display_var.get())
            self.display_var.set(str(self.result))
        elif button_text == "C":
            self.result = 0
            self.current = 0
            self.operator = ""
            self.display_var.set("0")
        else:
            if self.display_var.get() == "0":
                self.display_var.set("")
            self.display_var.set(self.display_var.get() + button_text)

root = tk.Tk()
calculator = Calculator(root)
root.mainloop()
