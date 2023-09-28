from tkinter import Tk, Toplevel,Frame,ttk,Text,DISABLED,Entry,NORMAL,Button
import serial.tools.list_ports
from os import system, path, remove
from pathlib import Path
from time import sleep
from sys import exit
import threading
import json

# import pyvista as pv
# from pyvistaqt import BackgroundPlotter,QtInteractor
# import numpy as np

from widgets import CustomMenuBar,CustomMenu
from widgets import Plotter_Frame,DRO_Frame,Serial_Console_Frame,Warning_Frame,Manual_Control_Frame
from widgets import Status_Bar
from serial_connection import serial_port

class RootWindow(Tk):

    def __init__(self,title):
        super().__init__()
        self.main_window=MainWindow(self,title)
        self.main_window.overrideredirect(1)
        self.attributes("-alpha",0.0)

        def onRootIconify(event):self.main_window.withdraw()
        self.bind("<Unmap>",onRootIconify)
        def onRootDeiconify(event):
            self.main_window.deiconify()
            self.main_window.lift()
        self.bind("<Map>",onRootDeiconify)
        self.bind("<FocusIn>",onRootDeiconify)

        self.main_window.lift()

class MainWindow(Toplevel):

    def __init__(self,parent,title):

        super().__init__(parent)
        self.parent=parent
        self.title(title)
        self.width=self.winfo_screenwidth()
        self.height=self.winfo_screenheight()
        self.geometry("{}x{}+{}+{}".format(self.width,self.height,0,0))
        self.resizable(False,False)
        self.menubar_bg="#2b2b2b"
        self.sidebars_bg="#303030"
        self.window_bg="#1b1b1b"
        self.file_item_bg="#404040"
        self.configure(background=self.window_bg)

        self.maximized=False

        self.connection=serial_port()

        self.MAX_FPS=30
        
        #encryption key
        self.key=None

        #file_options flag
        self.file_options_menu=None

        #load settings
        with open("settings.json","r") as f:
            self.settings=json.load(f)

        #menubar
        self.menubar=CustomMenuBar(self,self.width,30,self.menubar_bg)
        self.menubar.place(x=0,y=0)

        # file menu
        self.file_menu=CustomMenu(self,bg=self.menubar_bg)
        self.file_menu.add_menu_item(label="Open GCode File")
        self.menubar.add_menu(label="File",menu=self.file_menu)

        # #Settings menu
        self.settings_menu=CustomMenu(self,bg=self.menubar_bg)
        # self.settings_menu.add_menu_item(label="Change key",command=self.change_key)
        # self.settings_menu.add_menu_item(label="Export Key")
        # self.settings_menu.add_menu_item(label="Import Key")
        # self.settings_menu.add_menu_item(label="Destroy vault")
        # self.settings_menu.add_menu_item(label="Export vault")
        # self.settings_menu.add_menu_item(label="Import vault")
        self.menubar.add_menu(label="Settings",menu=self.settings_menu)

        # tools menu
        self.tools_menu=CustomMenu(self,bg=self.menubar_bg)
        self.menubar.add_menu(label="Tools",menu=self.tools_menu)

        # status bar
        self.status_bar=Status_Bar(self,width=self.width-10,height=30)
        self.status_bar.place(x=5,y=self.height-35)
        self.status_bar.set_text('Disconnected')
        # self.status_bar=Frame(self)
        # self.status_bar.configure(width=self.width-10,height=30)
        # self.status_bar.place(x=5,y=self.height-35)

        # home frame
        # port + baudrate +connect/disconnect buttons at the top
        # then 3 columns for console+serial log, DRO, graphic representation
        # below that, manual control and surface mapping 
        
        
        self.home_frame=Frame(self)
        self.home_frame_w=self.width-10
        self.home_frame_h=self.height-75
        self.home_frame.configure(width=self.home_frame_w,height=self.home_frame_h)
        self.home_frame.place(x=5,y=35)

        # port selecttion
        port_list=[]
        for port in serial.tools.list_ports.comports():
            port_list.append(port.device)
        self.port_dropdown=ttk.Combobox(self.home_frame,state='readonly',values=port_list)
        self.port_dropdown.current(0)
        self.port_dropdown.place(x=10,y=10,height=25)

        # baud selection
        self.baud_dropdown=ttk.Combobox(self.home_frame,state='readonly',values=['9600','14400','19200','38400','57600','115200','250000'])
        self.baud_dropdown.current(0)
        self.baud_dropdown.place(x=20+self.port_dropdown.winfo_reqwidth(),y=10,height=25)

        # connect/disconnect button
        self.connect_btn=ttk.Button(self.home_frame,text="Connect",command=self.connect)
        self.connect_btn.place(x=30+self.baud_dropdown.winfo_reqwidth()+self.port_dropdown.winfo_reqwidth(),y=10)

        # serial console
        self.serial_console=Serial_Console_Frame(self.home_frame,self.connection,width=(self.home_frame_w-40)//3,height=(self.home_frame_h-40)//2)
        self.serial_console.place(x=10,y=40)

        # Graphic representation
        self.plotter_frame=Plotter_Frame(self.home_frame,width=(self.home_frame_w-40)//3,height=(self.home_frame_h-40)//2)
        self.plotter_frame.place(x=20+self.serial_console.winfo_reqwidth(),y=40)

        # "DRO" and homming
        self.dro_frame=DRO_Frame(self.home_frame,width=(self.home_frame_w-40)//3,height=(self.home_frame_h-40)//2)
        self.dro_frame.place(x=30+self.serial_console.winfo_reqwidth()+self.plotter_frame.winfo_reqwidth(),y=40)
        self.dro_frame.set_process_command_funtion(self.serial_console.send_command)

        # # self.test_warning=Warning_Frame(self.home_frame,warning_message="This is a warning",width=500,height=200)
        # # self.test_warning.place(x=(self.width-500)//2,y=(self.height-200)//2)


        self.manual_control=Manual_Control_Frame(self.home_frame,width=260,height=235)
        self.manual_control.place(x=self.home_frame_w-270,y=50+((self.home_frame_h-40)//2))
        self.manual_control.set_command_handler(self.serial_console.send_command)

        self.bind('<Control-d>',self.quit)

        self.update_frames()

    def update_frames(self):
        if self.connection.is_connected():
            self.dro_frame.update_frame(self.serial_console.get_machine_pos())
        self.after(1000,self.update_frames)


    def connect(self):
        if not self.connection.is_connected():
            self.connection.config(port=self.port_dropdown.get(),baudrate=self.baud_dropdown.get())
            self.connection.connect()
            self.serial_console.connect()
            # self.serial_console.update_console()
            self.status_bar.set_text(f'Connected: {self.port_dropdown.get()}, {self.baud_dropdown.get()}')
            self.connect_btn.config(text="Disconnect")
        else:
            self.connection.disconnect()
            self.status_bar.set_text('Disconnected')
            self.connect_btn.config(text="Connect")
            self.serial_console.write_to_console('DISCONNECTED')
 
    # def load_graphics(self):
    #     # Create a PyVista QtInteractor

    #     self.plotter = BackgroundPlotter(window_size=(200,100))
    #     self.plotter.renderer.background_color = "white"


    #     # Define the dimensions of the grid
    #     x_min, x_max = 0,20
    #     y_min, y_max = 0,10
    #     n_points = 200  # Adjust this to match the grid you generated

    #     # Create a grid of x and y values
    #     x_grid = np.linspace(x_min, x_max, n_points)
    #     y_grid = np.linspace(y_min, y_max, n_points)
    #     x_grid, y_grid = np.meshgrid(x_grid, y_grid)

    #     # Define a function for the flat surface (you can use any function)
    #     # For example, a flat surface at z = 0
    #     z_grid = np.zeros_like(x_grid)

    #     # Optionally, add some noise to the surface for realism
    #     noise_amplitude = 0.05
    #     z_grid += np.random.normal(scale=noise_amplitude, size=z_grid.shape)

    #     # Create a PyVista structured grid
    #     grid = pv.StructuredGrid(x_grid, y_grid, z_grid)

    #     # Add the grid to the PyVista plotter
    #     self.plotter.add_mesh(grid, cmap="viridis")
    #     # Create a PyVistaQt interactor and embed it in the Toplevel window
    #     interactor = QtInteractor(self.plotter)
    #     interactor.interactor.Initialize()
    #     interactor.interactor.Start()
    
    #     self.plotter.place(x=300,y=50)
    #     # plotter_widget.pack(fill=tk.BOTH, expand=True)

    #     # #Help menu
    #     # # self.menubar.add_menu(label="Help")

    #     # #file panel
    #     # self.file_panel=CustomFileFrame(self,width=200,height=self.height-30,bg=self.sidebars_bg)
    #     # self.file_panel.place(x=0,y=30)
        
    #     # self.file_panel.add_files(self.vault)
    #     # self.bind_files()

    def move_window(self,x,y):
        self.geometry("{}x{}+{}+{}".format(self.width,self.height,x,y))

    def quit(self,*args):
        exit()