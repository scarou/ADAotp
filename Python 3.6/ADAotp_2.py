#coding:utf-8

import serial
import tkinter
from tkinter import messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import csv
import datetime
import os


LARGE_FONT = ("Verdana",12)
NORM_FONT = ("Verdana",10)
SMALL_FONT = ("Verdana",8)

style.use('seaborn-darkgrid')


# --- default values ---
port_COM = 'com14'
baud_rate = 115200
sample_size = 50
aruino_data = serial.Serial()    #Creating our serial object named aruino_data
big_data = {}

data_filename = 'Data_log.csv'
save_data_flg = False
save_inital_data_flg = False

fig = Figure()

a = fig.add_subplot(221)
b = fig.add_subplot(222)
c = fig.add_subplot(223)
d = fig.add_subplot(224)

subplot_array = [a,b,c,d]


def graphInit():
	# global subplot_array
	# for serie in subplot_array :
	# 	serie.set_title('Temp')
	a.clear()
	a.set_title('Temperature')

	a.set_ylim((0,80))
	a.set_ylabel (u'Temperature (°C)')

	# b.clear()
	# b.set_title('Current')
	# b.set_ylim(0,1000)
	# b.set_ylabel ('current (mA)')

	# c.clear()
	# c.set_title('Hydrogen')
	# c.set_ylim(0,1000)
	# c.set_ylabel ('Hydrogen (ppm)')
	
	# d.clear()
	# d.set_title('Pressure')
	# d.set_ylim(0,100)
	# d.set_ylabel ('Pressure (KPa)')


def askForValue(title_text, message, initial_value):
	"""
	Show a popup message with an entry and a default value
	"""
	popup_frame = tkinter.Tk()
	popup_frame.wm_title(title_text)
	label = tkinter.Label(popup_frame, text=message)
	label.pack(side='top', fill='x', pady=10)
	popup_entry =  tkinter.Entry(popup_frame)
	popup_entry.insert(0,initial_value)
	popup_entry.pack()
	popup_entry.select_range(0,'end')
	popup_entry.focus_set()

	def callback():
		global new_value
		new_value = popup_entry.get()
		# print(f'New value is now {new_value}')
		popup_frame.quit()
			
	popup_button = tkinter.Button(popup_frame, text = 'submit', width = 10, command= callback)
	popup_button.pack()
	popup_frame.mainloop()
	popup_frame.destroy()
	return new_value


def big_data_init():
	"""
	Return an initialized dictionnary with serieNameList as keys
	"""
	try:
		raw_values_array = serial_to_array()
		series_name_list = raw_values_array[0::3]
		# print(series_name_list)
		return create_series_dictionary(series_name_list)
	except Exception as e:
		raise


def choose_baud_rate():
	"""
	Ask for and return a new baud rate speed
	"""
	global baud_rate
	baud_rate = int(askForValue('Choose baudrate speed.','Specify the baud rate value.',baud_rate))
	print(f'New baud rate is : {baud_rate}')
	# return newBaudRate
		

def choose_port_com():
	"""
	Ask for and return a new port COM
	"""
	global port_COM
	port_COM = askForValue('Choose a serial port.','Choose the serial port to listen.',port_COM[3:])
	port_COM = 'com' + str(port_COM)
	print(f'New port COM is : {port_COM}')
	# return newPortCom


def choose_sample_size():
	"""
	Ask for and return a new sample size
	"""
	global sample_size
	sample_size = int(askForValue('Choose sample size.','Specify the sample size.',sample_size))
	print(f'New sample size is : {sample_size}')
	# return sample_size


def clean_string(string_to_clean,char_to_remove):
	"""
	Remove unwanted character from a string.
	"""
	string_to_clean = string_to_clean.rstrip(char_to_remove)
	return string_to_clean


def clear_subplot(array_of_subplot): 
	"""
	Clear all subplot in array_of_subplot
	"""
	for subPlot in array_of_subplot:
		subPlot.clear()

def format_subplot(array_of_subplot):
	"""
	Format all subplot in array_of_subplot
	"""


def create_series_dictionary(series_name_list):
	"""
	Create a dictionnary with the series_name_list as keys
	"""
	localDict = {}
	for seriesName in series_name_list:
		localDict[seriesName] = []
		# print (seriesName)
	return localDict


def open_serial_connection(port_COM,baud_rate,open_state):
	"""
	If open_state = True then open a serial connection of port_COM at baud_rate speed.
	If open_state = False then close serial connection.
	"""
	# serialStatusResult = serialStatus()
	if open_state == True:
		if aruino_data.isOpen() == False:
			aruino_data.port = port_COM
			aruino_data.baudrate = baud_rate
			try:
				aruino_data.open()
			except:
				messagebox.showerror('Ouch !',f'Unable to open serial port {aruino_data.port}. Please check connection.')
			else:
				print(f'Port {aruino_data.port} is now opened')
	elif open_state == False:
		if aruino_data.isOpen() == True:
			try:
				aruino_data.close()
			except:
			 	messagebox.showerror('Damn !',f'Unable to close serial port {aruino_data.port}. Please check connection.')
			else:
				print(f'Port {aruino_data.port} is now closed')
		else:
			messagebox.showinfo('Hey buddy !','Serial port already closed.')


def resize_sample(series_name_list_to_resize, sample_size):
	"""
	Resize each array of data according to the sample size value.
	"""
	while(len(big_data[series_name_list_to_resize[0]]) > sample_size):
		for serie_name in series_name_list_to_resize:
			big_data[serie_name].pop(0)


def save_data_as_CSV(state): # 
	"""
	Create a new csv file for saving data.
	"""
	global data_filename
	global save_data_flg
	if aruino_data.isOpen() == True:
		if state == True and save_data_flg == False: # Create the file name.
			print("START recording data...")
			data_filename = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
			save_data_flg = True
			print(data_filename)
		elif state == False and save_data_flg == True: # Close the csv file and rename it with the actual time code format.
			save_data_flg = False
			data_filename_closed = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
			os.rename(data_filename, data_filename_closed)
			print("STOP recording data and saving record as csv file.")
			print(data_filename_closed)
	else:
		messagebox.showinfo('Come on buddy...','No serial port opened. No data to record!')


def serial_to_array():
	"""
	Listen the serial connection and return an array of data
	"""
	if aruino_data.isOpen() == True:
		while (aruino_data.inWaiting()==0):     # Wait here until there is data
			pass

		arduino_string = aruino_data.readline()  # read the line of text from the serial port
		arduino_string = arduino_string.decode('utf-8') # Decode the Byte type data to str data. Needed with python 3.4 and later
		data_array = arduino_string.split(',')    # Split it into an array called data_array
		# print(data_array, type(data_array))
		return data_array


def animate(i):
	"""
	
	"""
	if aruino_data.isOpen() == True:
		global big_data

		if len(big_data) == 0:
			big_data = big_data_init()
			print(f'BigData initialized with {len(big_data)} series.')
				
		while (aruino_data.inWaiting() == 0):
			pass

		raw_values_array = serial_to_array()
		serie_values_list = raw_values_array[1::3]
		series_name_list = raw_values_array[0::3] # Maybe not the most efficient place to put it...

		for keyName, value in zip(series_name_list, serie_values_list):
			big_data[keyName].append(float(value))

		# print(big_data[series_name_list[0]])
		# graphInit()
		
		# print(f'animate : {subplot_array}')

		clear_subplot(subplot_array)

		# a.clear()
		a.set_title('Temperature')
		a.set_ylim(10,80)
		a.set_ylabel (u'Temperature (°C)')
		a.plot(big_data[series_name_list[0]],'ro-', label=u'Temp °C' , linewidth=0.5 , markersize=2)

		# b.clear()
		b.plot(big_data[series_name_list[1]], 'b^-', label='Current mA', linewidth=1 , markersize=2)
		b.set_title('Current')
		b.set_ylim(0,1000)
		b.set_ylabel ('current (mA)')

		# c.clear()
		c.plot(big_data[series_name_list[2]], 'g^-', label='Hydrogen', linewidth=1 , markersize=2)
		c.set_title('Hydrogen')
		c.set_ylim(0,1000)
		c.set_ylabel ('Hydrogen (ppm)')
		
		# d.clear()
		d.plot(big_data[series_name_list[3]], 'm^-', label='Pressure', linewidth=1 , markersize=2)
		d.set_title('Pressure')
		d.set_ylim(0,100)
		d.set_ylabel ('Pressure (KPa)')

		series_lengh = len(big_data[series_name_list[0]])

		if series_lengh > sample_size:
			resize_sample(series_name_list, sample_size)

		if save_data_flg == True:
			global save_inital_data_flg
			my_file = open(data_filename,'a', newline='')

			if save_inital_data_flg == False:
				try:
					the_writer = csv.writer(my_file, dialect='excel')
					i = 0
					while  i < len(big_data[series_name_list[0]]):
						the_writer.writerow([
							big_data[series_name_list[0]][i],
							big_data[series_name_list[1]][i],
							big_data[series_name_list[2]][i],
							big_data[series_name_list[3]][i]
							])
						i += 1
					save_inital_data_flg = True
				finally:
					my_file.close()

			else:
				try:
					the_writer = csv.writer(my_file, dialect='excel')  
					the_writer.writerow([
						big_data[series_name_list[0]][-1],
						big_data[series_name_list[1]][-1],
						big_data[series_name_list[2]][-1],
						big_data[series_name_list[3]][-1]
						])
				finally:
					my_file.close()



class DataLogApp(tkinter.Tk):
	"""
	Design the main application window and menu bar
	"""

	def __init__(self, *arg, **kwargs):# DataLogApp class can receive all arguments (*arg) and all method (**kwargs) of the mother class tkinter.Tk
		tkinter.Tk.__init__(self, *arg, **kwargs) # Call initialisation of the mother class tkinter.Tk and transmit all arguments (*arg) and all method (**kwargs)

		tkinter.Tk.wm_title(self, "Analogue Data Acquisition of the poor")

		# create a frame to put the menu in
		container = tkinter.Frame(self) 
		container.pack(side='top', fill="both", expand = True)
		
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0,weight=1)

		# create a container named "menu_bar" that will contain all menu items
		menu_bar = tkinter.Menu(container)

		# --- File menu ---
		file_menu = tkinter.Menu(menu_bar, tearoff=0)															# create a Menu element named "file_menu"
		file_menu.add_command(label="Save settings", command = lambda: messagebox.showinfo('Sorry...','Not supported just yet!'))	# add a command button/label labelled "Save setting"
		file_menu.add_separator()																			# add a separator horizontal line in the menu "file_menu"
		file_menu.add_command(label="Exit", command = quit)													# add a command button/label labelled "Exit" and assign the quit command to it
		menu_bar.add_cascade(label="File", menu=file_menu)													# add the file_menu element to the menu_bar element

		# --- Record data menu ---
		data_menu = tkinter.Menu(menu_bar, tearoff=1)														# create a Menu element named "data_menu"
		data_menu.add_command(label="Parameters", command = lambda: self.show_frame(ParamPage))
		data_menu.add_command(label="Start record", command = lambda: save_data_as_CSV(True)) 					# add a command button/label labelled
		data_menu.add_command(label="Stop record", command = lambda: save_data_as_CSV(False)) 					# add a command button/label labelled
		data_menu.add_command(label="Sample size", command = choose_sample_size) 								# add a command button/label labelled
		data_menu.add_command(label="Clear data", command = lambda: messagebox.showinfo('Sorry...','Not supported just yet!')) 	# add a command button/label labelled 
		menu_bar.add_cascade(label="Data", menu=data_menu)													# add the data_menu element to the menu_bar element

		# --- Serial port communication menu ---
		serial_port_menu = tkinter.Menu(menu_bar, tearoff=1)										# create a Menu element named "serial_port_menu"
		serial_port_menu.add_command(label='Choose port ...', command = choose_port_com)			# add a command button/label labelled "Choose serial port"
		serial_port_menu.add_command(label= 'Choose baud rate... ', command = choose_baud_rate)		# add a command button/label labelled "Choose baud rate"
		serial_port_menu.add_command(label='Open Serial COM...', command = lambda: open_serial_connection(port_COM,baud_rate,True))	# add a command button/label labelled "Start listening"
		serial_port_menu.add_command(label='Close Serial COM...', command = lambda: open_serial_connection(port_COM,baud_rate,False))	# add a command button/label labelled "Start listening"
 
		menu_bar.add_cascade(label="Serial port", menu=serial_port_menu) 						# add the serial_port_menu element to the menu_bar element


		tkinter.Tk.config(self, menu=menu_bar)

		self.frames = {}

		pages_dictionary = {StartPage, GraphPage, ParamPage}

		for F in pages_dictionary:
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky="nsew")
		self.show_frame(StartPage)

	def show_frame(self, cont): # show_frame is a method of DataLogApp
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

		button1 = tkinter.Button(self, text="Agree", command=lambda: controller.show_frame(GraphPage))
		button1.pack()
		button2 = tkinter.Button(self, text="Disagree", command=quit)
		button2.pack()


class ParamPage(tkinter.Frame):
	"""
	Create the parameters page
	"""

	def __init__(self, parent, controller):

		tkinter.Frame.__init__(self,parent) # Call initialisation of the mother class tkinter.Frame and transmit the parent name

		label = tkinter.Label(self, text="\nParameters\n", font= LARGE_FONT)
		label.grid(row = 0, column = 0, pady=10,padx=10)

		check_one = tkinter.Checkbutton(self)
		check_one.grid(row = 1, column = 0)
		entry_1 = tkinter.Entry(self, text = "entry 1")
		entry_1.grid(row = 1, column = 1)
		entry_2 = tkinter.Entry(self, text = "entry 2")
		entry_2.grid(row = 1, column = 2)
		entry_3 = tkinter.Entry(self, text = "entry 3")
		entry_3.grid(row = 1, column = 3)
		entry_4 = tkinter.Entry(self, text = "entry 4")
		entry_4.grid(row = 1, column = 4)
		entry_5 = tkinter.Entry(self, text = "entry 5")
		entry_5.grid(row = 1, column = 5)

		button1 = tkinter.Button(self, text="Ok", command=lambda: controller.show_frame(GraphPage))
		button1.grid(row = 6, column = 2)


class SerieParameter():
	"""
	Create a class to define parameter of a data serie
	"""


class GraphPage(tkinter.Frame): # GraphPage is a "daughter" of the "mother" class tkinter.Frame it will inherit all attributs of Frame class within tkinter
	"""
	Create the graph monitoring page.
	"""

	def __init__(self, parent, controller):

		tkinter.Frame.__init__(self,parent) # Call initialisation of the mother class tkinter.Frame and transmit the parent name
		
		self.rowconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)

		tkinter.Label(self, text = 'Monitoring Page', font=("Verdana",14), padx =10, pady =15).grid(row=0,column=3, rowspan =2)

		self.record_data_Label = tkinter.Label(self, text = 'Record data as .csv',font=("Verdana",12))
		self.start_btn = tkinter.Button(self, text = 'START',  padx =10, pady =5,command = self.start_btn_click)
		self.stop_btn = tkinter.Button(self, text = 'STOP', background= "red",relief="sunken", padx =10, pady =5,command = self.stop_btn_click)

		# port_COM.trace("w", update_label)

		# def update_label(*args):
		#     var_port_com_label.set(port_COM)

		var_port_com_label = tkinter.StringVar()
		var_port_com_label.set(port_COM)
		self.port_com_label = tkinter.Label(self, text = 'COM14',textvariable=var_port_com_label, padx =5, pady =5)

		# self.serialLbl = tkinter.Label(self, text = 'Serial',font=("Verdana",12))
		# self.baud_rateLbl = tkinter.Label(self, text = '115200', padx =5, pady =5)
		# self.connectionLbl = tkinter.Label(self, text = 'OPEN', bg='green', padx =10, pady =5)

		self.record_data_Label.grid(row = 0, column = 0, columnspan = 3)
		# self.serialLbl.grid(row = 0, column = 4, columnspan = 3)
		self.start_btn.grid(row = 1, column = 1)
		self.stop_btn.grid(row = 1, column =2 )
		self.port_com_label.grid(row=1,column=4, sticky='e')
		# self.baud_rateLbl.grid(row=1,column=5)
		# self.connectionLbl.grid(row=1,column=6)

		# création d'un widget 'Canvas' pour l'affichage des graphiques :
		self.canvas = FigureCanvasTkAgg(fig, self)
		self.canvas.draw

		self.canvas.get_tk_widget().grid(row =2, column =0)

		# toolbar = NavigationToolbar2TkAgg(can1, self)
		# toolbar.update()
		self.canvas._tkcanvas.grid(row =2, column =0, columnspan =7, padx =5, pady =5, sticky='nswe')


	def start_btn_click (self):
		if aruino_data.isOpen() == True:
			self.start_btn.configure(background= "green",relief="sunken")
			self.stop_btn.configure(background= "SystemButtonFace",relief="raised")
			save_data_as_CSV(True)
		else:
			# popupmsg('No serial port opened. No data to record!')
			messagebox.showinfo('Come on buddy...','No serial port opened. No data to record!')

	def stop_btn_click (self):
		self.start_btn.configure(background= "SystemButtonFace",relief="raised")
		self.stop_btn.configure(background= "red",relief="sunken")
		save_data_as_CSV(False)


app = DataLogApp() # Create an instance of DataLogApp

# center app window
screen_x = app.winfo_screenwidth()
screen_y = app.winfo_screenheight()
window_x = 1280
window_y = 720
posX = (screen_x//2)-(window_x//2)
posY = (screen_y//2)-(window_y//2)
geo = f"{window_x}x{window_y}+{posX}+{posY}"
app.geometry(geo)

ani = animation.FuncAnimation(fig, animate, interval=800)

app.mainloop()




# open_serial_connection(port_COM,baud_rate,True)
# raw_values_array = serial_to_array()

# series_name_list = raw_values_array[0::3]
# # print (len(big_data))
# if len(big_data) == 0:
# 	big_data = big_data_init()
# 	print(f'BigData initialized with {len(big_data)} series.')
# # print (len(big_data))


# # print(type(big_data))
# # print(big_data)
# n = int(input("Loop number ?"))
# for i in range(0,n):
# 	raw_values_array = serial_to_array()
# 	serie_values_list = raw_values_array[1::3]
# 	for keyName, value in zip(series_name_list, serie_values_list):
# 		big_data[keyName].append(value+ str(i))
# 	print(f'Loop # : {i}')
	

# for key,value in big_data.items():
# 	print (key,value)

# input()

# open_serial_connection(port_COM,baud_rate,False)

