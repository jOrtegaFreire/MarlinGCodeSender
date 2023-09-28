from tkinter import Button,Entry,Text,Frame,Label,Toplevel,ttk
from tkinter import END, W,DISABLED,NORMAL
from PIL.ImageTk import PhotoImage
from time import time
from PIL import Image
import json

from serial_connection import serial_port
import GCODE

# from pyvistaqt import QtInteractor

class CustomMenuBar(Frame):

    def __init__(self,container:Toplevel,width=1,height=1,bg="Black"):
        self.container=container
        self.width=width
        self.height=height
        self.bg=bg
        self.menus=[]
        self.x=0
        self.init_x_pos=None
        self.init_y_pos=None

        super().__init__(self.container,width=self.width,height=self.height)
        self.configure(background=self.bg)
        self.minimizeBtn=ControlBtn(self,"minimizeBtn",command=container.parent.iconify)
        self.maximizeBtn=ControlBtn(self,"maximizeBtn")
        self.closeBtn=ControlBtn(self,"closeBtn",command=container.quit)

        self.minimizeBtn.place(x=self.width-90,y=0)
        self.maximizeBtn.place(x=self.width-60,y=0)
        self.closeBtn.place(x=self.width-30,y=0)

        self.bind('<Button-1>',self.set_init_pos)
        # self.bind('<B1-Motion>',self.move_window)

    def update_resolution(self,width):
        self.width=width
        self.configure(width=self.width)
        self.minimizeBtn.place(x=self.width-90,y=0)
        self.maximizeBtn.place(x=self.width-60,y=0)
        self.closeBtn.place(x=self.width-30,y=0)

    def set_init_pos(self,event):
        start_x, start_y = event.widget.winfo_pointerxy()
        self.init_diff_x_pos=start_x
        self.init_diff_y_pos=start_y

    # def move_window(self,event):
    #     start_x, start_y = event.widget.winfo_pointerxy()
    #     self.container.move_window(diff_x,diff_y)

    def add_menu(self,label="Menu Item",width=1,height=1,menu=None,command=None):
        self.menus.append(CustomMenuButton(self,label=label,menu=menu,command=command,x=self.x))
        self.menus[-1].place(x=self.x,y=0,height=self.height)
        self.x+=self.menus[-1].winfo_reqwidth()

#custom button class for minimize,maximize and close window buttons
class ControlBtn(Button):

    def __init__(self,container,image_name,command=None):
        self.container=container
        super().__init__(container,bd=0,highlightthickness=0,activebackground=container.bg,command=command)
        self.img1=PhotoImage(Image.open("images/"+image_name+"1.png"))
        self.img2=PhotoImage(Image.open("images/"+image_name+"2.png"))
        self.configure(image=self.img1)

        self.bind("<Enter>",self.on_enter)
        self.bind("<Leave>",self.on_leave)

    def on_enter(self,event):self.configure(image=self.img2)
    def on_leave(self,event):self.configure(image=self.img1)

#custom class for menu bar item
class CustomMenuButton(Button):

    def __init__(self,container,label="Menu Button",menu=None,command=None,x=0):
        self.container=container
        self.menu=menu
        self.x=x
        self.active=False
        super().__init__(container,text=label,font=("System",12),bg=container.bg,fg="#c4c4c4",
                        bd=0,activebackground="#9a9a9a",activeforeground="#c4c4c4",highlightbackground="#9a9a9a")

        self.bind("<Button-1>",self.on_click)
        self.bind("<Enter>",self.on_enter)
        self.bind("<Leave>",self.on_leave)

    def on_click(self,event):
        for menu in self.container.menus:
            if menu!=self and menu.active:
                menu.active=False
                menu.toggle()
        self.active=not self.active
        self.toggle()
    def on_enter(self,event):self.configure(bg="#4e4e4e")
    def on_leave(self,event):self.configure(bg=self.container.bg)
    def toggle(self):self.menu.toggle(self.x)

#custom class for menu bar menu
class CustomMenu(Frame):
    def __init__(self,container,height=30,bg="Black"):
        super().__init__(container,height=height,bg=bg)
        self.container=container
        self.bg=bg
        self.width=0
        self.menu_items=[]
        self.y=0
        self.visible=False

    def add_menu_item(self,label="menu item",command=None):
        self.menu_items.append(CustomMenuItem(self,label=label,y=self.y,command=command))
        self.y+=self.menu_items[-1].winfo_reqheight()
        self.configure(height=self.y)
        if self.menu_items[-1].winfo_reqwidth()>self.width:
            self.width=self.menu_items[-1].winfo_reqwidth()
            self.configure(width=self.width)
        for menu_item in self.menu_items:
            menu_item.place(x=0,y=menu_item.y,width=self.width)
    
    def toggle(self,x):
        if self.visible:
            self.place_forget()
            self.visible=False
        else:
            self.place(x=x,y=30)
            self.tkraise()
            self.visible=True


class CustomMenuItem(Button):

    def __init__(self,container,label="menu item",y=0,command=None):
        self.container=container
        self.y=y
        super().__init__(container,text=label,font=("System",12),bg=container.bg,fg="#c4c4c4",anchor=W,
                        bd=0,activebackground="#9a9a9a",activeforeground="#c4c4c4",highlightbackground="#9a9a9a",
                        command=command)

        self.bind("<Enter>",self.on_enter)
        self.bind("<Leave>",self.on_leave)

    def on_enter(self,event):self.configure(bg="#4e4e4e")
    def on_leave(self,event):self.configure(bg=self.container.bg)

class CustomFileFrame(Frame):

    def __init__(self,container,width=1,height=1,bg="Black"):
        self.files=[]
        self.item_height=10
        self.width=width
        self.text_width=int(self.width/8)
        self.bg=bg
        super().__init__(container,width=width,height=height,bg=bg)


    def add_file(self,vault):
        file=list(vault)[-1]
        self.files.append(FileItem(self,label=file,ext=vault[file]))
        self.item_height=self.files[-1].winfo_reqheight()
        self.files[-1].place(x=0,y=(len(vault)-1)*self.item_height,width=self.width)

    def add_files(self,vault):
        for idx,file in enumerate(vault):
            self.files.append(FileItem(self,label=file,ext=vault[file]))
            self.item_height=self.files[-1].winfo_reqheight()
            self.files[-1].place(x=0,y=idx*self.item_height,width=self.width)


class FileItem(Button):
    def __init__(self,container,label="file_name",ext=None,height=1):
        self.container=container
        self.file_name=label
        self.ext=ext
        super().__init__(container,font=("Courier",10),width=container.width,height=height,bg=container.bg,
                    fg="#c4c4c4",activebackground="#9a9a9a",bd=0)
        self.set_text()

    def set_text(self):
        self.configure(text=self.file_name[:self.container.text_width-4]+'...',anchor=W)

class FileItemOptions(Frame):

    def __init__(self,container,width=1,height=1,bg="Black",file_item=None):
        self.container=container
        self.file_item=file_item
        self.width=width
        self.height=height
        self.bg=bg
        super().__init__(container,width=width,height=height,bg=bg)

        self.openBtn=Button(self,text="Open",font=("Courier",10),bg=self.bg,fg="#c4c4c4",activebackground="#9a9a9a",
                        bd=0,highlightthickness=0,command=self.open_file,padx=10,pady=5,anchor=W)
        self.extractBtn=Button(self,text="Extract",font=("Courier",10),bg=self.bg,fg="#c4c4c4",activebackground="#9a9a9a",
                        bd=0,highlightthickness=0,command=self.extract_file,padx=10,pady=5,anchor=W)
        self.deleteBtn=Button(self,text="Delete",bg=self.bg,font=("Courier",10),fg="#c4c4c4",activebackground="#9a9a9a",
                        bd=0,highlightthickness=0,command=self.delete_file,padx=10,pady=5,anchor=W)

        self.openBtn.place(x=0,y=0,width=self.width)
        self.extractBtn.place(x=0,y=self.extractBtn.winfo_reqheight(),width=self.width)
        self.deleteBtn.place(x=0,y=2*self.extractBtn.winfo_reqheight(),width=self.width)

        self.openBtn.bind('<Enter>',self.on_enter)
        self.extractBtn.bind('<Enter>',self.on_enter)
        self.deleteBtn.bind('<Enter>',self.on_enter)
        self.openBtn.bind('<Leave>',self.on_leave)
        self.extractBtn.bind('<Leave>',self.on_leave)
        self.deleteBtn.bind('<Leave>',self.on_leave)

    #highlight on mouse hoover
    def on_enter(self,event):event.widget.configure(bg="#505050")
    #highlight on mouse hoover
    def on_leave(self,event):event.widget.configure(bg=self.bg)
    #show pop up menu 
    def show(self,x,y):self.place(x=x,y=y)
    #open file
    def open_file(self):
        self.container.open_file(self.file_item.file_name)
        self.destroy()
    #extract file to decrypted folder
    def extract_file(self):
        self.container.extract(self.file_item.file_name)
        self.destroy()
    def delete_file(self):
        print("deliting "+self.file_name+"."+self.file_item.ext)
        self.destroy()

class ProgressFrame(Frame):

    def __init__(self,container,width=1,height=1,bg="Black",label="Progress"):
        self.container=container
        self.width=width
        self.height=height
        self.bg=bg
        super().__init__(container,width=width,height=height,bg=bg)
        self.progressBarFrame=Frame(self,width=self.width-200,height=50,bg=self.bg)
        self.progressBar=Frame(self.progressBarFrame,width=100,height=50,bg="#505050")
        self.speed=10
        self.message=Label(self,text=label,font=("Courier",18),bg=self.bg,
                            fg="Gray")
        self.progressBar.place(x=0,y=0)
        self.progressBarFrame.place(x=(int(self.width-self.progressBarFrame.winfo_reqwidth())/2),
                                    y=int((self.height-self.progressBarFrame.winfo_reqheight())/2))
        self.message.place(x=int((self.width-self.message.winfo_reqwidth())/2),
                            y=int((self.height-self.progressBarFrame.winfo_reqheight())/2)+75)

    def show(self):
        self.place(x=0,y=0)
        self.wait_visibility()
        self.tkraise()
        self.animate()

    def animate(self):
        if self.progressBar.winfo_x()+self.progressBar.winfo_reqwidth()>=self.width-200 and self.speed>0:
            self.speed*=-1
        elif self.progressBar.winfo_x()<=0 and self.speed<0:
            self.speed*=-1
        self.progressBar.place(x=self.progressBar.winfo_x()+self.speed,y=0)
        self.after(10,self.animate)


class Plotter_Frame(Frame):

    def __init__(self,container,width=1,height=1):
        super().__init__(container,width=width,height=height,background="black")
        self.container=container

        # Create a PyVistaQt interactor and embed it in the Tkinter Frame
        # self.plotter = QtInteractor(self, size=(width,height))
        # self.plotter.set_background("white")

class ReadOnlyEntry(Entry):

    def __init__(self,container,**kwargs):
        super().__init__(container,kwargs)
        self.config(state=DISABLED,bg=kwargs.get('bg'))

    def write(self,text):
        self.config(state=NORMAL)
        self.delete(0,'end')
        self.insert('end',text)
        self.config(state=DISABLED)

class ReadOnlyText(Text):

    def __init__(self,container,**kwargs):
        super().__init__(container,kwargs)
        self.config(state=DISABLED)

    def write(self,text,end='\n'):
        self.config(state=NORMAL)
        self.insert('end',text+end)
        self.yview_moveto(1.0)
        self.config(state=DISABLED)

    def clear(self):
        self.config(state=NORMAL)
        self.delete(0.0,'end')
        self.config(state=DISABLED)
        self.yview_moveto(1.0)


class DRO_Frame(Frame):

    def __init__(self,container,**kwargs):
        super().__init__(container,kwargs)
        self.container=container
        self.bg="#505050"
        self.width=kwargs.get('width')
        self.height=kwargs.get('height')

        # process command function
        self.process_command=None

        self.xpos_entry=ReadOnlyEntry(self,font=("Arial",32),width=9,justify='right')
        self.xpos_entry.write('+300.0000')
        self.xpos_entry.place(x=121,y=0)

        self.ypos_entry=ReadOnlyEntry(self,font=("Arial",32),width=9,justify='right')
        self.ypos_entry.write('0.0000')
        self.ypos_entry.place(x=121,y=10+self.xpos_entry.winfo_reqheight())

        self.zpos_entry=ReadOnlyEntry(self,font=("Arial",32),width=9,justify='right')
        self.zpos_entry.write('0.0000')
        self.zpos_entry.place(x=121,y=20+self.xpos_entry.winfo_reqheight()+self.ypos_entry.winfo_reqheight())

        self.home_icon=PhotoImage(Image.open("images/home_icon.png"))
        self.home_x_btn=Button(self,image=self.home_icon,bg=self.bg,activebackground=self.bg,
                                bd=0,command=lambda command=GCODE.HOME_X: self.process_command(command))
        self.home_x_btn.place(x=131+self.xpos_entry.winfo_reqwidth(),y=0)

        self.home_y_btn=Button(self,image=self.home_icon,bg=self.bg,activebackground=self.bg,
                                bd=0,command=lambda command=GCODE.HOME_Y: self.process_command(command))
        self.home_y_btn.place(x=131+self.xpos_entry.winfo_reqwidth(),y=10+self.xpos_entry.winfo_reqheight())

        self.home_z_btn=Button(self,image=self.home_icon,bg=self.bg,activebackground=self.bg,
                                bd=0,command=lambda command=GCODE.HOME_Z: self.process_command(command))
        self.home_z_btn.place(x=131+self.xpos_entry.winfo_reqwidth(),y=20+self.xpos_entry.winfo_reqheight()+self.ypos_entry.winfo_reqheight())

        # zero axis btns
        self.zero_x_btn=Button(self,text='Zero\nX',font=("Arial",16),command=lambda command=GCODE.SET_X_0:self.process_command(command))
        self.zero_x_btn.place(x=61,y=0,width=51,height=51)

        self.zero_y_btn=Button(self,text='Zero\nY',font=("Arial",16),command=lambda command=GCODE.SET_Y_0:self.process_command(command))
        self.zero_y_btn.place(x=61,y=10+self.xpos_entry.winfo_reqheight(),width=51,height=51)

        self.zero_z_btn=Button(self,text='Zero\nZ',font=("Arial",16),command=lambda command=GCODE.SET_Z_0:self.process_command(command))
        self.zero_z_btn.place(x=61,y=20+self.xpos_entry.winfo_reqheight()+self.ypos_entry.winfo_reqheight(),width=51,height=51)

        self.zero_all_btn=Button(self,text='Z\ne\nr\no\n\nA\nl\nl',font=("Arial",14))
        self.zero_all_btn.place(x=0,y=0,width=51,height=177)


    def set_process_command_funtion(self,process_command_function):
        self.process_command=process_command_function

    def update_frame(self,machine_pos:tuple):
        self.xpos_entry.write(f'{machine_pos[0]:.4f}')
        self.ypos_entry.write(f'{machine_pos[1]:.4f}')
        self.zpos_entry.write(f'{machine_pos[2]:.4f}')


class Serial_Console_Frame(Frame):

    def __init__(self,container:Frame,connection:serial_port,**kwargs):
        super().__init__(container,kwargs)
        self.container=container
        self.connection=connection
        self.width=kwargs.get('width')
        self.height=kwargs.get('height')

        # active flag
        self.active=True

        # ABSOLUTE/RELATIVE FLAG
        self.absolute=True

        # MACHINE AXIS INFO
        self.x_pos=0
        self.y_pos=0
        self.z_pos=0

        # self.console_log=Text(self,width=47,height=16)
        self.console_log=ReadOnlyText(self,width=47,height=16)
        self.console_log.place(x=0,y=0,width=self.width,height=self.height-30)
        self.console_cmd=Entry(self,width=50)
        self.console_cmd.place(x=0,y=self.height-25,width=self.width-60,height=25)
        self.clear_console_btn=Button(self,text="Clear",command=self.clear_console)
        self.clear_console_btn.place(x=self.width-50,y=self.height-25,width=50,height=25)

        self.console_cmd.bind('<Return>',self.send_command_from_console)

        # self.update()

    def connect(self):
        self.console_log.write('CONNECTING',end='')
        self.wait_connect(True)

    def wait_connect(self,condition:bool):
        if condition:
            self.console_log.write('.',end='')
            line=self.connection.readline()
            self.after(200,self.wait_connect,line=='')
        else:
            self.console_log.write('\nCONNECTED')
            self.after(200,self.get_machine_grettings)

    def get_machine_grettings(self):
        while True:
            data=self.connection.readline()
            if data=='':break
            self.console_log.write(data)
        self.console_log.write('READY')

    def send_command_from_console(self,event):
        text=self.console_cmd.get()
        self.console_cmd.delete(0,'end')
        self.console_log.write('[HOST]:'+text)
        if self.connection.write(text):
            self.update_machine_position(text)
            self.wait_response(True,'',False)
        else:self.write_to_console('Connection error')

    def update_machine_position(self,command:str):
        if GCODE.ABSOLUTE_MODE in command:self.absolute=True
        if GCODE.RELATIVE_MODE in command:self.absolute=False
        if GCODE.LINEAR_MOVE_0 in command or GCODE.LINEAR_MOVE_1 in command:
            if 'X' in command or 'Y' in command or 'Z' in command:
                commands=command.split(' ')
                x,y,z=None,None,None
                for _command in commands[1:]:
                    if 'X' in _command:x=float(_command[1:])
                    if 'Y' in _command:y=float(_command[1:])
                    if 'Z' in _command:z=float(_command[1:])
                if self.absolute:
                    self.x_pos=self.x_pos if x is None else x
                    self.y_pos=self.y_pos if y is None else y
                    self.z_pos=self.z_pos if z is None else z
                else:
                    self.x_pos=self.x_pos if x is None else self.x_pos+x
                    self.y_pos=self.y_pos if y is None else self.y_pos+y
                    self.z_pos=self.z_pos if z is None else self.z_pos+z

    def wait_response(self,condition:bool,response,background:bool):
        if condition:
            line=self.connection.readline()
            self.after(100,self.wait_response,line=='',line,background)
        else:
            self.process_response(True,response,background)

    def process_response(self,condition,response,background:bool):
        if condition:
            if response!='' and not background:
                if 'echo:' in response:self.console_log.write(response[5:])
                else:self.console_log.write(response)
            if 'X:' in response and 'Y:' in response and 'Z:' in response:
                data=response.split(' ')
                self.x_pos=float(data[0][2:])
                self.y_pos=float(data[1][2:])
                self.z_pos=float(data[2][2:])
            if response=='ok':return
            line=self.connection.readline()
            self.after(50,self.process_response,line!='ok',line,background)
        else:
            if not background:self.console_log.write(response)

    def pause(self):
        self.active=False

    def resume(self):
        self.active=True

    def clear_console(self):
        self.console_log.clear()

    def send_command(self,command:str,background=False):
        if self.connection.write(command):
            self.update_machine_position(command)
            self.wait_response(True,'',background)
        else:self.write_to_console('Connection error')

    def write_to_console(self,msg:str,end='\n'):
        self.console_log.write(msg,end=end)

    def process_command(self,command):
        self.write_to_console('[HOST]: '+command)
        self.send_command(command)

    def get_machine_pos(self):
        return self.x_pos,self.y_pos,self.z_pos

class Warning_Frame(Frame):

    def __init__(self,container,warning_message='',**kwargs):
        super().__init__(container,kwargs)
        self.msg=warning_message
        self.config(background="#1b1b1b")
        self.msg_label=Label(self,text=self.msg,font=("Arial",16),bg="#1b1b1b",fg="white")
        self.msg_label.place(x=(self.winfo_reqwidth()-self.msg_label.winfo_reqwidth())//2,y=50)
        self.accept_btn=Button(self,text='Accept',font=("Arial",16),bg="#2c2c2c",fg="white",activebackground="#3d3d3d",
                               activeforeground="white",bd=0,command=self.destroy)
        self.accept_btn.place(x=(self.winfo_reqwidth()-self.accept_btn.winfo_reqwidth())//2,y=120)

        self.grab_set()

class Status_Bar(Frame):
    
    def __init__(self,container,**kwargs):
        super().__init__(container,kwargs)
        self.width=kwargs.get('width')
        self.height=kwargs.get('height')
        
        self.status_text=Label(self,font=("Arial",10),anchor='w',borderwidth=2,relief='sunken')
        self.status_text.place(x=2,y=2,width=self.width-4,height=self.height-4)

    def set_text(self,text):
        # self.status_text.write(text)
        self.status_text.configure(text=text)

class Manual_Control_Frame(Frame):
    
    def __init__(self,container,**kwargs):
        super().__init__(container,kwargs)
        self.width=kwargs.get('width')
        self.height=kwargs.get('height')

        self.serial_command_handler=None

        self.acc_combobox=ttk.Combobox(self,state='readonly',values=['0.1','1.0','10.0','50.0'])
        self.acc_combobox.current(2)
        self.acc_combobox.place(x=10,y=10,height=25)

        self.up_img=PhotoImage(Image.open("images/up_btn.png"))
        self.down_img=PhotoImage(Image.open("images/down_btn.png"))
        self.left_img=PhotoImage(Image.open("images/left_btn.png"))
        self.right_img=PhotoImage(Image.open("images/right_btn.png"))


        self.x_up_btn=Button(self,image=self.right_img,borderwidth=0,
                             command=lambda command=f'G1 X':self.process_command(command))
        self.x_down_btn=Button(self,image=self.left_img,borderwidth=0,
                               command=lambda command=f'G1 X-':self.process_command(command))
        self.x_down_btn.place(x=10,y=120,width=50,height=50)
        self.x_up_btn.place(x=130,y=120,width=50,height=50)

        self.y_up_btn=Button(self,image=self.up_img,borderwidth=0,
                             command=lambda command=f'G1 Y':self.process_command(command))
        self.y_down_btn=Button(self,image=self.down_img,borderwidth=0,
                               command=lambda command=f'G1 Y-':self.process_command(command))
        self.y_up_btn.place(x=70,y=65,width=50,height=50)
        self.y_down_btn.place(x=70,y=175,width=50,height=50)

        self.z_up_btn=Button(self,image=self.up_img,borderwidth=0,
                             command=lambda command=f'G1 Z':self.process_command(command))
        self.z_down_btn=Button(self,image=self.down_img,borderwidth=0,
                               command=lambda command=f'G1 Z-':self.process_command(command))
        self.z_up_btn.place(x=200,y=65,width=50,height=50)
        self.z_down_btn.place(x=200,y=175,width=50,height=50)

    def set_command_handler(self,command_handler):
        self.serial_command_handler=command_handler

    def process_command(self,command):
        command=f'{command}{self.acc_combobox.get()}'
        self.serial_command_handler('G91',background=True)
        self.serial_command_handler(command,background=True)
        self.serial_command_handler('G90',background=True)

# class Settings_Frame(Frame):

#     def __init__(self,container,settings:dict(),**kwargs):
#         super().__init__(container,kwargs)
#         self.settings=settings

#         self.warning_frame=
        