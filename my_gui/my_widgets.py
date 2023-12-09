import customtkinter
from datetime import datetime
from collections import OrderedDict

class my_entry_button():
    def __init__(self, master, entry_row=1,entry_column=1,button_row=1,button_column=2,padding=5):
        pdng = padding
        # create entry
        self.entry = customtkinter.CTkEntry(master=master, placeholder_text="CTkEntry",border_width=1)
        self.entry.grid(row=entry_row, column=entry_column, padx=(pdng, pdng), pady=(pdng, pdng), sticky="nsew")
        # create button
        self.button = customtkinter.CTkButton(master=master, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.button.grid(row=button_row, column=button_column, padx=(pdng, pdng), pady=(pdng, pdng), sticky="nsew")

class my_console(customtkinter.CTkTextbox):
    def __init__(self, master,
                 row, column,
                 columnspan=None,
                 padx=1, pady=1,
                 sticky='news'):
        super().__init__(master=master, font=('Roboto',14,'bold'))
        self.grid(row=row, column=column,
                  columnspan=columnspan,
                  padx=padx, pady=pady,
                  sticky=sticky)

    def display(self,date_time=False, texte="",color='red'):
        if date_time==True:
            time = datetime.now()
            texte = str(time) + ': ' + texte

        if type(texte) == str:
            self.textbox_print(texte,color)

        elif type(texte) == bytes:
            texte = str(texte)
            texte = texte[2:len(texte) - 5]
            self.textbox_print(texte,color)

        elif type(texte) == list:
            for item in texte:
                self.textbox_print(texte,color)

        elif type(texte) == dict or type(texte) == OrderedDict:
            for item in texte:
                self.textbox_print(item + " : " + str(texte[item]) + '\n', color)

    def textbox_print(self,texte,color):
        self.tag_config('text_color', foreground=color)
        self.insert('end', texte+'\n',tags='text_color')

    def clear(self):
        self.delete("1.0", "end")
