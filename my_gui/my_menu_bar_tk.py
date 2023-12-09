import tkinter as tk
from tkinter import messagebox

class CustomMenubar(tk.Menu):
    def __init__(self, master=None):
        super().__init__(master)

        # Create the "File" menu

        # menu = tk.Menu(self, tearoff=0)
        # # self.master.config(menu=menu)
        # booking = tk.Menu(menu)
        # file = tk.Menu(menu)
        # statistics = tk.Menu(menu)
        # file.add_command(label="Exit", font=("", 50))
        # statistics.add_command(label="Age", font=("", 50))
        # statistics.add_command(label="Gender", font=("", 50))
        # statistics.add_command(label="Interests", font=("", 50))
        # menu.add_cascade(label="Booking", menu=booking, font=("", 50))
        # menu.add_cascade(label="File", menu=file, font=("", 50))
        # menu.add_cascade(label="Statistics", menu=statistics, font=("", 50))

        file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", font=("Arial",12), menu=file_menu)
        file_menu.add_command(label="New", font=("Arial",12), command=self.on_new_file,)
        file_menu.add_command(label="Open", font=("Arial",12), command=self.on_open_file)
        file_menu.add_command(label="Save", font=("Arial",12), command=self.on_save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", font=("Arial",12), command=self.on_exit)

        # Create additional menus and commands as needed

    def on_new_file(self):
        messagebox.showinfo("New File", "Creating a new file...")

    def on_open_file(self):
        messagebox.showinfo("Open File", "Opening a file...")

    def on_save_file(self):
        messagebox.showinfo("Save File", "Saving the file...")

    def on_exit(self):
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.master.destroy()
