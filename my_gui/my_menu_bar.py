"""
Customtkinter Menu Bar
Author: Akash Bora
"""

import customtkinter

class menu_bar(customtkinter.CTkFrame):
    def __init__(self, master,fg_color='transparent',height=25, width=10, padx=5, pady=2):
        super().__init__(master=master,fg_color=fg_color)
        self.fg_color = fg_color
        self.after(10)
        self.num = 0
        self.height = height
        self.width = width
        self.padx = padx
        self.pady = pady
        self.menu = []

    def add_cascade(self, text=None, **kwargs):
        if text is None:
            text = f"Menu {self.num+1}"

        self.menu_button = customtkinter.CTkButton(master=self, fg_color=self.fg_color, width=self.width, height=self.height, text_color=("gray10", "#DCE4EE"),text=text)
        self.menu_button.grid(row=0, column=self.num, padx=(self.padx,0), pady=self.pady, sticky='news')
        self.num += 1

        return self.menu_button

    def configure(self, **kwargs):
        if "bg_color" in kwargs:
           self.configure(fg_color=kwargs.pop("bg_color"))
        self.configure(**kwargs)