# !/usr/bin/python3.5

import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.font import Font

from PIL import Image, ImageTk

response = ''


def gui(question, dir, know):
    root = Tk()
    root.title("Title")
    root.geometry('420x500')

    time26 = Font(family = 'Helvetica', size = 18)

    tkinter.font

    def resize_image(event):
        factor = 0.9
        new_width = 400  # int(event.width*factor)
        new_height = 300  # int(event.height*factor)
        image = copy_of_image.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        label.config(image = photo)
        label.image = photo  # avoid garbage collection

    image = Image.open(dir)
    copy_of_image = image.copy()
    photo = ImageTk.PhotoImage(image)
    label = ttk.Label(root, image = photo)
    label.bind('<Configure>', resize_image)
    label.grid(row = 0, columnspan = 2, sticky = "nsew")

    # label.pack(fill=BOTH, expand = YES)
    # label.grid(row=0)

    def resp(i):
        global response
        if int(i) == 1:
            response = 1
        elif int(i) == 0:
            response = 0
        elif int(i) == 3:
            response = 'x'
        else:
            response = inputbox.get()
        print(response, i)
        root.destroy()

    known = know
    if known:
        label1 = tkinter.Label(root, text = question, font = time26).grid(row = 1, columnspan = 2)
        button = tkinter.Button(root, text = 'Yes', width = 25, command = lambda: resp(1))
        button.grid(row = 2, column = 0)
        button2 = tkinter.Button(root, text = 'No', width = 25, command = lambda: resp(0))
        button2.grid(row = 2, column = 1)

    else:
        label1 = tkinter.Label(root, text = question, font = time26)
        label1.grid(row = 1, columnspan = 2)

        inputbox = tkinter.Entry(root)
        inputbox.grid(row = 2, column = 0)
        #     print(inputbox.get())
        button2 = tkinter.Button(root, text = 'Okay', width = 25, command = lambda: resp(2)).grid(row = 2, column = 1)
        button3 = tkinter.Button(root, text = 'Unknown/Others', width = 25, command = lambda: resp(3))
        button3.grid(row = 3, columnspan = 2)

    root.grid_columnconfigure(0, minsize = 200)
    root.grid_columnconfigure(1, minsize = 120)
    root.grid_rowconfigure(0, minsize = 100)
    root.grid_rowconfigure(1, minsize = 50)
    root.grid_rowconfigure(2, minsize = 50)
    root.mainloop()
    return str(response)
