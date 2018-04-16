# -*- coding: UTF-8 -*-
"""
Version python 3.6

import <module_name>                        -->     Need to refer to <module_name> inorder to use inclued functions e.g. serial.Serial()
from <module_name> import <function_name>   -->     The <function_name> can be used directly without reference to its <module_name>
from <module_name> import *                 -->     All the the functions inclued in the <module_name>
                                                    can be used used directly without reference to its <module_name>
"""
import random # Used for create_plots function (test purpose)
import serial # Need to make a refrence to it in order to use one of its function e.g. serial.Serial()

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter #as tk
from tkinter import messagebox
##import ttk

import csv
import datetime
import os


T1_Arr=[]  # Create an empty array for saving temperatures values
I1_Arr=[]  # Create an empty array for saving current values
H1_Arr=[]  # Create an empty array for saving Hydrogen values
P1_Arr=[]  # Create an empty array for saving Hydrogen values

sensorList = [T1_Arr,I1_Arr,H1_Arr,P1_Arr]


LARGE_FONT = ("Verdana",12)
NORM_FONT = ("Verdana",10)
SMALL_FONT = ("Verdana",8)

style.use('seaborn-darkgrid')

# --- default values ---
portCOM = 'com14'
baudRate = 115200
sampleSize = 50

arduinoData = serial.Serial()    #Creating our serial object named arduinoData
# ---

dataFileName = 'Data_log.csv'
saveData = False
saveInitalData = False


f = Figure()

##a = f.add_subplot(111)
##b = f.add_subplot(111)
##c = f.add_subplot(111)
##d = f.add_subplot(111)

a = f.add_subplot(221)
b = f.add_subplot(222)
c = f.add_subplot(223)
d = f.add_subplot(224)

subPlotArr = [a,b,c,d]

# --------------------------
# function for test purposes only

def qf(stringtoprint): # print a text in the python shell
    print(stringtoprint)
    
def create_plots(plotNumber, amplitude): # create random x, y values ; need random lib
    xs = []
    ys = []

    for i in range(plotNumber):
        x = i
        y= random.randrange(amplitude)

        xs.append(x)
        ys.append(y)
    return xs, ys

# --------------------------


def choosePort(): # Allow the user to choose the serial port for serial communication
    
    if arduinoData.isOpen() == True:
        print (arduinoData.isOpen())
        messagebox.showinfo('Not allowed !',f'Serial port {portCOM} already opened. Close connection prior to change port.')

    else:
        portComQ =tkinter.Tk()
        portComQ.wm_title('Serial port?')
        label = tkinter.Label(portComQ, text = "Choose the serial port to listen.")
        label.pack(side="top", fill="x", pady=10)
        

        e = tkinter.Entry(portComQ)
        e.insert(0,portCOM[3:]) # Getting the port number from the String
        e.pack()
        e.focus_set()

        def callback():
            global portCOM
            portCOM = 'com' + str(e.get())
            print(f'Port {portCOM} is now selected.')
            portComQ.destroy()
            
        b = tkinter.Button(portComQ, text='Submit', width=10, command=callback)
        b.pack()
        tkinter.mainloop()
    

def chooseBaudRate(): # Allow the user to choose the baud rate of the serial communication
    if arduinoData.isOpen() == True:
        print (arduinoData.isOpen())
        messagebox.showinfo('Not allowed !',f'Serial port {portCOM} already opened at {baudRate} baud.\nClose connection prior to change baud rate.')

    else:
        baudRateQ =tkinter.Tk()
        baudRateQ.wm_title('Baud rate?')
        label = tkinter.Label(baudRateQ, text = "Specify the baud rate value.")
        label.pack(side="top", fill="x", pady=10)

        e = tkinter.Entry(baudRateQ)  
        e.insert(0,baudRate)
        e.pack()
        e.focus_set()

        def callback():
            global baudRate
            baudRate = e.get()
            print(f'{baudRate} baudrate is now selected')
            baudRateQ.destroy()
            
        b = tkinter.Button(baudRateQ, text='Submit', width=10, command=callback)
        b.pack()
        tkinter.mainloop()


def chooseSampleSize(): # Allow the user to choose the sample size of displayed values
    sampleSizeQ =tkinter.Tk()
    sampleSizeQ.wm_title('Sample size?')
    label = tkinter.Label(sampleSizeQ, text = "Specify the sample size of displayed values.")
    label.pack(side="top", fill="x", pady=10)

    e = tkinter.Entry(sampleSizeQ)
    e.insert(0,sampleSize)
    e.pack()
    e.focus_set()
    

    def callback():
        global sampleSize
        sampleSize = int(e.get())
        print(f'Sample size is now {sampleSize}')
        sampleSizeQ.destroy()

##    e.bind("<Return>", callback)
        
    b = tkinter.Button(sampleSizeQ, text='Submit', width=10, command=callback)
    b.pack()
    tkinter.mainloop()
    

# --- Now working !!! ---
def openSerialPort(portCom, baudRate, openState): # Should open a serial communication with the portCom and baudRate defined
    global arduinoData
    
    if openState == True:
        if arduinoData.isOpen() == False:
            arduinoData.port = portCOM
            arduinoData.baudrate = baudRate
            try:
                arduinoData.open()
            except:
                messagebox.showerror('Ouch !',f'Unable to open serial port {arduinoData.port}. Please check connection.')
            else:
                print(f'Port {arduinoData.port} is now opened')
                
    elif openState == False:
        if arduinoData.isOpen() == True:
            try:
                arduinoData.close()
            except:
                messagebox.showerror('Damn !',f'Unable to close serial port {arduinoData.port}. Please check connection.')
            else:
                print(f'Port {arduinoData.port} is now closed')
        else:
            messagebox.showinfo('Hey buddy !','Serial port already closed.')
            
# -----------------------    

    

def saveDataAsCSV(state): # Create a new csv file for saving data.
    global dataFileName
    global saveData
    if arduinoData.isOpen() == True:
        
        if state == True and saveData == False: # Create the file name.
            print("START recording data...")
            dataFileName = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
            saveData = True
            print(dataFileName)
            
        elif state == False and saveData == True: # Close the csv file and rename it with the actual time code format.
            saveData = False
            dataFileNameClosed = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
            os.rename(dataFileName, dataFileNameClosed)
            print("STOP recording data and saving record as csv file.")
            print(dataFileNameClosed)
    else:
        messagebox.showinfo('Come on buddy...','No serial port opened. No data to record!')

        
def popupmsg(msg): # Popup the given message "msg"
    print(msg)
    popup = tkinter.Tk()

    popup.wm_title("!")
    label = tkinter.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10, anchor="center")
    B1 = tkinter.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
    

def clearSubPlot(subPlotToClear): # Clear all subplot in 
    for subPlot in subPlotToClear:
        subPlot.clear()
        

def storeSensorData(dataToStore, listToAppend ):    # Store received sensor values <dataToStore> to the list to append <listToAppend>
    for i in range(len(dataToStore)):
        listToAppend[i].append(float(dataToStore[i]))


def resizeSample(arrayListToResize, sampleSize):
    while(len(arrayListToResize[0])>sampleSize):     
        for i in range(len(arrayListToResize)):
            arrayListToResize[i].pop(0)         # If you have "sampleSize" or more points, delete the first one from the array
    
    
def animate(i): # This function create graph, read data from serial port and update the graph
    if arduinoData.isOpen() == True:
        while (arduinoData.inWaiting()==0):     # Wait here until there is data
            pass
            
        arduinoString = arduinoData.readline()  # read the line of text from the serial port

        arduinoString = arduinoString.decode('utf-8') # Decode the Byte type data to str data. Needed with python 3.4 and later

        dataArray = arduinoString.split(',')    # Split it into an array called dataArray

        storeSensorData(dataArray, sensorList)
        
        clearSubPlot(subPlotArr) # clean the last graph in order to allow the new values to be drawn

        
        a.plot(T1_Arr, 'ro-', label=u'Temp °C' , linewidth=0.5 , markersize=2)   # plot the temperature data
        a.set_title('Temperature')
        a.set_ylim(10,80)
        a.set_ylabel (u'Temperature (°C)')
        
        b.plot(I1_Arr, 'b^-', label='Current mA', linewidth=1 , markersize=2) # plot the current data
        b.set_title('Current')
        b.set_ylim(0,1000)
        b.set_ylabel ('current (mA)')
        
        c.plot(H1_Arr, 'g^-', label='Hydrogen', linewidth=1 , markersize=2) # plot hydrogen data
        c.set_title('Hydrogen')
        c.set_ylim(0,1000)
        c.set_ylabel ('Hydrogen (ppm)')
        
        d.plot(P1_Arr, 'm^-', label='Pressure', linewidth=1 , markersize=2) # plot pressure data
        d.set_title('Pressure')
        d.set_ylim(0,100)
        d.set_ylabel ('Pressure (KPa)')

        
        if (len(sensorList[0]) > sampleSize):
               resizeSample(sensorList, sampleSize)
              
        
        if saveData ==True: # --- Saving data as csv file --- (see saveDataAsCSV)
            global saveInitalData
            myFile = open(dataFileName,'a', newline='')
            
            if saveInitalData == False:
                try:
                    theWriter = csv.writer(myFile, dialect='excel')
                    i = 0
                    while  i < len(T1_Arr):
                        
                        theWriter.writerow([T1_Arr[i],I1_Arr[i],H1_Arr[i],P1_Arr[i]])
                        i += 1
                    saveInitalData = True
                finally:
                    myFile.close()
                    
            else:
                try:
                    theWriter = csv.writer(myFile, dialect='excel')  
                    theWriter.writerow([T1_Arr[-1],I1_Arr[-1],H1_Arr[-1],P1_Arr[-1]]) # Write the last element of the array
                finally:
                    myFile.close()


class DataLogApp(tkinter.Tk): # DataLogApp inherit all attributs of Tk class within tkinter
    """
    Design the main application window and menubar
    """

    def __init__(self, *arg, **kwargs): # DataLogApp class can receive all arguments (*arg) and all method (**kwargs) of the mother class tkinter.Tk

        tkinter.Tk.__init__(self, *arg, **kwargs) # Call initialisation of the mother class tkinter.Tk and transmit all arguments (*arg) and all method (**kwargs)

        tkinter.Tk.wm_title(self, "Analogue Data Acquisition of the poor")

        container = tkinter.Frame(self) # create a frame to put the menu in
        container.pack(side='top', fill="both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0,weight=1)


        #  test déclaration StringVar...
        maVariableTest = tkinter.StringVar()
        maVariableTest.set('1ere valeur test DataLogApp')
        print(f'maVariableTest = {maVariableTest.get()}')

        menubar = tkinter.Menu(container)                        # create a container named "menubar" that will contain all menu items
        
        # --- File menu ---
        filemenu = tkinter.Menu(menubar, tearoff=0)              # create a Menu element named "filemenu"
        filemenu.add_command(label="Save settings", command = lambda: popupmsg("Not supported just yet!")) # add a command button/label labelled "Save setting"
        filemenu.add_separator()                            # add a separator horizontal line in the menu "filemenu"
        filemenu.add_command(label="Exit", command = quit)  # add a command button/label labelled "Exit" and assign the quit command to it
        menubar.add_cascade(label="File", menu=filemenu)    # add the filemenu element to the menubar element

        # --- Record data menu ---
        data_menu = tkinter.Menu(menubar, tearoff=1)       # create a Menu element named "data_menu"
        data_menu.add_command(label="Start record",   # add a command button/label labelled
                                command = lambda: saveDataAsCSV(True)) 
        data_menu.add_command(label="Stop record",    # add a command button/label labelled
                                command = lambda: saveDataAsCSV(False)) 
        data_menu.add_command(label="Sample size",  # add a command button/label labelled
                                command = chooseSampleSize) 
        data_menu.add_command(label="Clear data",       # add a command button/label labelled 
                                command = lambda: popupmsg("Not supported just yet!")) 
        menubar.add_cascade(label="Data",               # add the data_menu element to the menubar element
                                 menu=data_menu)

        
        # --- Serial port communication menu ---
        serialPort_menu = tkinter.Menu(menubar, tearoff=1)      # create a Menu element named "serialPort_menu"
        serialPort_menu.add_command(label='Choose port ...',    # add a command button/label labelled "Choose serial port"
                                command = choosePort)
        serialPort_menu.add_command(label= 'Choose baud rate... ', # add a command button/label labelled "Choose baud rate"
                                command = chooseBaudRate)
        serialPort_menu.add_command(label='Open Serial COM...',     # add a command button/label labelled "Start listening"
                                command = lambda: openSerialPort(portCOM,baudRate,True))
        serialPort_menu.add_command(label='Close Serial COM...',     # add a command button/label labelled "Start listening"
                                command = lambda: openSerialPort(portCOM,baudRate,False))
 
        menubar.add_cascade(label="Serial port",                    # add the serialPort_menu element to the menubar element
                                 menu=serialPort_menu) 

        

        tkinter.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, graph_Page):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

        



class StartPage(tkinter.Frame): # Start page is a "daughter" of the "mother" class tkinter.Frame
    """
    Create the Start page
    """

    def __init__(self, parent, controller): 

        tkinter.Frame.__init__(self,parent) # Call initialisation of the mother class tkinter.Frame and transmit the parent name

        label = tkinter.Label(self, text="""\nPython 3.6 version of ADAotp\n
        \nAnalogue Data Acquisition of the poor\n
        \nUse at your own risk.\nThere is no promise of waranty.\n""", font= LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tkinter.Button(self,
                            text="Agree",
                            command=lambda: controller.show_frame(graph_Page))
        button1.pack()
        button2 = tkinter.Button(self,
                            text="Disagree",
                            command=quit)
        button2.pack()





class graph_Page(tkinter.Frame): # graph_Page is a "daughter" of the "mother" class tkinter.Frame it will inherit all attributs of Frame class within tkinter
    """
    Create the graph monitoring page.
    """

    def __init__(self, parent, controller):

        tkinter.Frame.__init__(self,parent) # Call initialisation of the mother class tkinter.Frame and transmit the parent name
        
        self.rowconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        
        tkinter.Label(self, text = 'Monitoring Page', font=("Verdana",14), padx =10, pady =15).grid(row=0,column=3, rowspan =2)

        self.recordDataLbl = tkinter.Label(self, text = 'Record data as .csv',font=("Verdana",12))
        self.startBtn = tkinter.Button(self, text = 'START',  padx =10, pady =5,command = self.startBtnClick)
        self.stopBtn = tkinter.Button(self, text = 'STOP', background= "red",relief="sunken", padx =10, pady =5,command = self.stopBtnClick)



        """ Cette partie est supposée afficher l'état de la connection série (exemple : SERIAL : "com14"  "115200 baud" "OPEN" )
        avec une mise à jour des infos à chaque changement de n° de port ou vitesse ou ouverture/fermeture du port série
        Ici, le n° de port com est changé par la fonction choosePort (voir def choosePort() plus haut) appelée par un bouton du
        menu "Serial port" et qui modifie la directement la variable PortCOM.
        Le probème, c'est que je ne parviens pas à détecter le changement de portCOM d'ici (portCOM est poutant bien la variable
        que je souhaite surveiller, mais si je tente une surveillance de la variable portCOM, j'ai un message d'erreur
        """
        # portCOM.trace("w", update_label)

        # def update_label(*args):
        #     var_portComLbl.set(portCOM)

        
        var_portComLbl = tkinter.StringVar()
        var_portComLbl.set(portCOM)
        self.portComLbl = tkinter.Label(self, text = 'COM14',textvariable=var_portComLbl, padx =5, pady =5)



        # self.serialLbl = tkinter.Label(self, text = 'Serial',font=("Verdana",12))
        # self.baudRateLbl = tkinter.Label(self, text = '115200', padx =5, pady =5)
        # self.connectionLbl = tkinter.Label(self, text = 'OPEN', bg='green', padx =10, pady =5)


        self.recordDataLbl.grid(row = 0, column = 0, columnspan = 3)
        # self.serialLbl.grid(row = 0, column = 4, columnspan = 3)
        self.startBtn.grid(row = 1, column = 1)
        self.stopBtn.grid(row = 1, column =2 )
        self.portComLbl.grid(row=1,column=4, sticky='e')
        # self.baudRateLbl.grid(row=1,column=5)
        # self.connectionLbl.grid(row=1,column=6)

        # création d'un widget 'Canvas' pour l'affichage des graphiques :
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw

        self.canvas.get_tk_widget().grid(row =2, column =0)

##        toolbar = NavigationToolbar2TkAgg(can1, self)
##        toolbar.update()
        self.canvas._tkcanvas.grid(row =2, column =0, columnspan =7, padx =5, pady =5, sticky='nswe')


    def startBtnClick (self):
        if arduinoData.isOpen() == True:
            self.startBtn.configure(background= "green",relief="sunken")
            self.stopBtn.configure(background= "SystemButtonFace",relief="raised")
            saveDataAsCSV(True)
        else:
            # popupmsg('No serial port opened. No data to record!')
            messagebox.showinfo('Come on buddy...','No serial port opened. No data to record!')

    def stopBtnClick (self):
        self.startBtn.configure(background= "SystemButtonFace",relief="raised")
        self.stopBtn.configure(background= "red",relief="sunken")
        saveDataAsCSV(False)


##        canvas = FigureCanvasTkAgg(f, self)
##        canvas.draw
##
##        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand = True)
##
##        toolbar = NavigationToolbar2TkAgg(canvas, self)
##        toolbar.update()
##        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        


app = DataLogApp()

# center app window
screen_x = app.winfo_screenwidth()
screen_y = app.winfo_screenheight()
window_x = 1280
window_y = 720
posX = (screen_x//2)-(window_x//2)
posY = (screen_y//2)-(window_y//2)
geo = f"{window_x}x{window_y}+{posX}+{posY}"
app.geometry(geo)

ani = animation.FuncAnimation(f, animate, interval=500)

app.mainloop()
