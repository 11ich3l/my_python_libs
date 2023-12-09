import customtkinter
# import tkinter
from my_gui import my_menu_bar_tk, my_widgets

# import my_dropdown_menu
# import my_menu_bar
# from customtkinter_menu_bar.CTkMenuBar import *

DEFAULT_PADDING = 10

COL_1 = 1
ROW_1 = 4

def gui_init(gui_obj):
    gui_obj.iconify()
    gui_obj.update()
    customtkinter.windows.CTk.wm_state(gui_obj, newstate="zoomed")
    gui_obj.mainloop()

class my_appearance():
    def __init__(self, master,appearance_text="Appearance Mode:", row=ROW_1, column=COL_1, padding=5):
        pdng = padding
        self.appearance_mode_label = customtkinter.CTkLabel(master, text=appearance_text)
        self.appearance_mode_label.grid(row=row, column=column, padx=pdng, pady=pdng)
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(master, values=["Light", "Dark", "System"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=row, column=column+1, padx=pdng, pady=pdng)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_default_color_theme("blue")
        customtkinter.set_appearance_mode(new_appearance_mode)

class my_color():
    def __init__(self, master, top, color_text="Color Mode:", row=ROW_1, column=COL_1, padding=5):
        pdng = padding
        self.master = master
        self.top = top
        print(str(master))
        self.color_mode_label = customtkinter.CTkLabel(master, text=color_text)
        self.color_mode_label.grid(row=row, column=column, padx=pdng, pady=pdng)
        self.color_mode_optionemenu = customtkinter.CTkOptionMenu(master, values=["blue", "green", "dark-blue"],command=self.change_color_mode_event)
        self.color_mode_optionemenu.grid(row=row, column=column + 1, padx=pdng, pady=pdng)

    def change_color_mode_event(self, new_color_mode: str):
        print("change_color_mode_event")
        if new_color_mode == "green":
            new_color_mode = r"C:\2-APPLICATIONS\PYTHON\Python311\Lib\site-packages\customtkinter\assets\themes\green.json"
        elif new_color_mode == "blue":
            new_color_mode = r"C:\2-APPLICATIONS\PYTHON\Python311\Lib\site-packages\customtkinter\assets\themes\blue.json"
        elif new_color_mode == "dark-blue":
            new_color_mode = r"C:\2-APPLICATIONS\PYTHON\Python311\Lib\site-packages\customtkinter\assets\themes\dark-blue.json"
        else:
            return
        self.top.destroy()
        self.top.__init__(new_color_mode)
        gui_init(self.top)

class simple_gui(customtkinter.CTk):
    def __init__(self, default_color):
        super().__init__()
        customtkinter.set_default_color_theme(default_color)
        dpdng = DEFAULT_PADDING

        # configure grid layout
        self.grid_columnconfigure(COL_1, weight=1)
        self.grid_columnconfigure(COL_1+1, weight=0)
        self.grid_rowconfigure(ROW_1-1, weight=0)
        self.grid_rowconfigure(ROW_1, weight=0)
        self.grid_rowconfigure(ROW_1+1, weight=1)
        self.grid_rowconfigure(ROW_1+2, weight=0)
        self.grid_rowconfigure(ROW_1+3, weight=0)

        # create main entry and button
        self.entry_button_1 = my_widgets.my_entry_button(self, entry_row=ROW_1, entry_column=COL_1, button_row=ROW_1, button_column=COL_1 + 1, padding=dpdng)

        # create console-textbox
        self.console_frame = customtkinter.CTkFrame(self, corner_radius=10,fg_color="gray23",border_width=1,border_color="#565B5E")
        self.console_frame.grid(row=ROW_1+1, column=COL_1,padx=dpdng, columnspan=2, sticky="nsew")
        self.console_frame.grid_rowconfigure(0, weight=0)
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_title = customtkinter.CTkLabel(self.console_frame,corner_radius=10,bg_color='transparent',fg_color='transparent',text="Console",height=10)
        self.console_title.grid(row=0, column=0,padx=10,pady=(1,0), sticky="nw")
        self.console = my_widgets.my_console(master=self.console_frame, row=1, column=0, sticky="nsew")
        self.console.configure(border_width=1)
        self.console.display(date_time=True,texte='Hello World !!',color='red')
        # self.textbox = customtkinter.CTkTextbox(self, width=250)
        # self.textbox.grid(row=ROW_1+1, column=COL_1, columnspan=2, padx=dpdng, pady=dpdng, sticky="nsew")

        # create progress bar
        self.progressbar_1 = customtkinter.CTkProgressBar(self,mode='indeterminate',height=10)
        self.progressbar_1.grid(row=ROW_1+2, column=COL_1, columnspan=2, padx=dpdng, pady=dpdng, sticky="news")
        self.progressbar_1.start()

        self.theme_frame = customtkinter.CTkFrame(self, fg_color='transparent')
        self.theme_frame.grid(row=ROW_1 + 3, column=COL_1 + 1, sticky="nse")
        # appearance mode
        self.appearance_frame = customtkinter.CTkFrame(self.theme_frame,fg_color='transparent')
        self.appearance_frame.grid(row=0, column=0, sticky="nse")
        self.appearance_mode = my_appearance(self.appearance_frame, appearance_text="Appearance: ")

        # color mode
        self.color_frame = customtkinter.CTkFrame(self.theme_frame, fg_color='transparent')
        self.color_frame.grid(row=0, column=1, sticky="nse")
        self.color_mode = my_color(self.color_frame, self, color_text="Color: ")

        # Menu bar
        # Create a custom menubar
        menubar = my_menu_bar_tk.CustomMenubar(self)
        self.config(menu=menubar)

        # my_menu_bar = tkinter.Menu(self)
        # m1 = tkinter.Menu(my_menu_bar, tearoff=0)
        # m1.add_command(label="Open File", command=lambda: print("Open"))
        # m1.add_separator()
        # m1.add_command(label="Save File", command=lambda: print("Save"))
        # self.config(menu=menu_bar)
        # self.menu_frame = customtkinter.CTkFrame(self, fg_color='transparent')
        # self.menu_frame.grid(row=0, column=0, rowspan=4, columnspan=3, sticky="nsew")
        # menu = CTkMenuBar(master=self.menu_frame)
        #
        # button_1 = menu.add_cascade("File")
        # button_2 = menu.add_cascade("Edit")
        # button_3 = menu.add_cascade("Settings")
        # button_4 = menu.add_cascade("About")
        #
        # dropdown1 = dropdown_menu.CustomDropdownMenu(widget=button_1)
        # dropdown1.add_option(option="Open", command=lambda: print("Open"))
        # dropdown1.add_option(option="Save")

        # dropdown1.add_separator()
        #
        # sub_menu = dropdown1.add_submenu("Export As")
        # sub_menu.add_option(option=".TXT")
        # sub_menu.add_option(option=".PDF")
        #
        # dropdown2 = my_dropdown_menu.CustomDropdownMenu(widget=button_2)
        # dropdown2.add_option(option="Cut")
        # dropdown2.add_option(option="Copy")
        # dropdown2.add_option(option="Paste")
        #
        # dropdown3 = my_dropdown_menu.CustomDropdownMenu(widget=button_3)
        # dropdown3.add_option(option="Preferences")
        # dropdown3.add_option(option="Update")
        #
        # dropdown4 = my_dropdown_menu.CustomDropdownMenu(widget=button_4)
        # dropdown4.add_option(option="Hello World")

        # menu.grid(row=0,column=1,sticky='nw')


