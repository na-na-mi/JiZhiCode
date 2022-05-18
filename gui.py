import tkinter as tk

from matplotlib.pyplot import text
top = tk.Tk()
top.title("Netflix")
top.geometry("800x600")
var = tk.StringVar()
l = tk.Label(top, textvariable=var, bg='green', font=('Arial', 12), width=30, height=2)
# 说明： bg为背景，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高
l.pack()
on_hit = False#先定义 然后全局变量才有意义
def hit_me():
    global on_hit
    if on_hit == False:
        on_hit = True
        var.set('you hit me')
    else:
        on_hit = False
        var.set('')
    #str = "chris evens:eat shit!"
    #print(str)
b = tk.Button(top, text='click me', font=('Arial', 12), width=10, height=1, command=hit_me)
b.pack()
top.mainloop()
