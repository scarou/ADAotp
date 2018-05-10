# coding:utf-8
import pdb

import serial
import tkinter
from tkinter import messagebox

import json

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import csv
import datetime
import os

matplotlib.use("TkAgg")

style.use('seaborn-darkgrid')

arduino_data = serial.Serial()  # Creating our serial object named arduino_data
config={}
dict_of_series = {}

save_data_flg = False
save_inital_data_flg = False

fig = Figure()


def add_subplots_config(arg1: object, arg2: object, arg3: object, arg4: object) -> object:
	global a, b, c, d, subplot_array
	fig.clf()
	a = fig.add_subplot(arg1)
	b = fig.add_subplot(arg2)
	c = fig.add_subplot(arg3)
	d = fig.add_subplot(arg4)
	subplot_array = [a, b, c, d]


add_subplots_config(arg1=221, arg2=222, arg3=223, arg4=224)


def value_compliance_check(attribut_name, value):
	"""
	Return a tuple "value" compliance to the specified rule "name"
	"""
	def name(value_to_test):
		try:
			casted_value = str(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not a string.")
			return False, value_to_test


	def units(value_to_test):
		""" ymin have to be an integer"""
		try:
			casted_value = str(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not a string.")
			return False, value_to_test

	def ylabel(value_to_test):
		""" ymin have to be an integer"""
		try:
			casted_value = str(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not a st.")
			return False, value_to_test

	def ymin(value_to_test):
		""" ymin have to be an integer"""
		try:
			casted_value = int(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not an integer.")
			return False, value_to_test

	def ymax(value_to_test):
		""" ymax have to be an integer"""
		try:
			casted_value = int(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not an integer.")
			return False, value_to_test

	def color(value_to_test):
		""" color have to be a matplotlib compatible value_to_test"""
		if value_to_test in config['available_colors']:
			return True, value_to_test
		else:
			print(f"Sorry, {value_to_test} is not an available color.")
			return False, value_to_test

	def marker(value_to_test):
		""" marker have to be a matplotlib compatible value_to_test"""
		if value_to_test in config['available_markers']:
			return True, value_to_test
		else:
			print(f"Sorry, {value_to_test} is not an available marker.")
			return False, value_to_test

	def line_style(value_to_test):
		""" line_style have to be a matplotlib compatible value_to_test"""
		if value_to_test in config['available_line_styles']:
			return True, value_to_test
		else:
			print(f"Sorry, {value_to_test} is not an available line style.")
			return False, value_to_test

	def line_size(value_to_test):
		""" line_size have to be a float"""
		try:
			casted_value = float(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not a float.")
			return False, value_to_test

	def marker_size(value_to_test):
		""" marker_size have to be a float"""
		try:
			casted_value = float(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not a float.")
			return False, value_to_test

	def graph_number(value_to_test):
		""" graph_number have to be an integer"""
		try:
			casted_value = int(value_to_test)
			return True, casted_value
		except:
			print(f"Sorry, {value_to_test} is not an integer.")
			return False, value_to_test

	rules_dictionary = {
		'name': name,
		'units': units,
		'ylabel': ylabel,
		'ymin': ymin,
		'ymax': ymax,
		'color': color,
		'marker': marker,
		'line_style': line_style,
		'line_size': line_size,
		'marker_size': marker_size,
		'graph_number': graph_number
	}

	return rules_dictionary.get(attribut_name)(value)


def ask_for_value(title_text, message, initial_value):
	"""
	Show a popup message with an entry and a default value
	"""
	popup_frame = tkinter.Tk()
	# pdb.set_trace()
	popup_frame.wm_title(title_text)
	label = tkinter.Label(popup_frame, text=message)
	label.pack(side='top', fill='x', pady=10)
	popup_entry = tkinter.Entry(popup_frame)
	popup_entry.insert(0, initial_value)
	popup_entry.pack()
	popup_entry.select_range(0, 'end')
	popup_entry.focus_set()

	def _on_enter(self):
		popup_button.focus_set()

	def callback(self):
		global new_value
		new_value = popup_entry.get()
		# print(f'New value is now {new_value}')
		popup_frame.quit()

	popup_button = tkinter.Button(popup_frame, text='submit', width=10)
	popup_button.pack()
	popup_entry.bind('<Return>', _on_enter)
	popup_button.bind('<Return>', callback)
	popup_button.bind('<Button-1>', callback)
	popup_frame.mainloop()

	popup_frame.destroy()
	return new_value


def dict_of_series_init() -> object:
	"""
	Return an initialized dictionnary with serieNameList as keys
	"""
	try:
		raw_values_array = serial_to_array()
		series_names_list = raw_values_array[0::3]
		# print(series_names_list)
		return create_series(series_names_list=series_names_list)
	except Exception as e:
		raise


def choose_baud_rate():
	"""
	Ask for and change the baud rate speed
	"""
	if arduino_data.isOpen():
		messagebox.showwarning("Serial connection running...","Please close serial connection prior to change baud rate value.")
	else:
		config['baud_rate'] = int(ask_for_value(
			title_text='Choose baudrate speed.',
			message='Specify the baud rate value.',
			initial_value=config['baud_rate']))
		ref_to_GraphPage.baud_rate_label.configure(text=config['baud_rate'])
		print(f"New baud rate is : {config['baud_rate']}")


def choose_port_com():
	"""
	Ask for and return a new port COM
	"""
	if arduino_data.isOpen():
		messagebox.showwarning("Serial connection running...","Please close serial connection prior to change portCOM value.")
	else:
		config['port_COM'] = ask_for_value(
			title_text='Choose a serial port.',
			message='Choose the serial port to listen.',
			initial_value=config['port_COM'][3:])
		config['port_COM'] = 'com' + str(config['port_COM'])
		ref_to_GraphPage.port_com_label.configure(text=config['port_COM'])
		print(f"New port COM is : {config['port_COM']}")


def choose_sample_size():
	"""
	Ask for and return a new sample size
	"""
	# global sample_size
	new_sample_size = int(ask_for_value(
		title_text='Choose sample size.',
		message='Specify the sample size.',
		initial_value=SensorSeries.sample_size))
	SensorSeries.change_sample_size(new_sample_size)
	print(f'New sample size is : {new_sample_size}')


def clear_subplot(array_of_subplot):
	"""
	Clear all subplot in array_of_subplot
	"""
	for subPlot in array_of_subplot:
		subPlot.clear()


def clear_data():
	""" Erase all data of each series """
	if dict_of_series != {}:
		if messagebox.askokcancel("Please confirm", "Are you sure you want to clear all actual data ?"):
			for serie in dict_of_series:
				dict_of_series[serie].data = []
				print(f"Data of serie {serie} cleared !")
		else:
			print("Ok, nothing this time...")
	else:
		messagebox.showinfo("Come on buddy...", "No serie to monitor... nothing to clear...")


def create_series(series_names_list):
	"""
	Create for each value of the serie_names list a SensorSerie instances
	and store it into dict_of_series dictionary
	"""
	dict_of_series = {}
	for serie in series_names_list:
		dict_of_series[serie] = SensorSeries(name=serie)
		print(f'{dict_of_series[serie].name} serie have been successfully created !')
	return dict_of_series


def open_serial_connection(open_state):
	"""
	If open_state = True then open a serial connection of port_COM at baud_rate speed.
	If open_state = False then close serial connection.
	"""
	if open_state is True:
		if arduino_data.isOpen() is False:
			arduino_data.port = config['port_COM']
			arduino_data.baudrate = config['baud_rate']
			try:
				arduino_data.open()
			except:
				messagebox.showerror('Ouch !',
									 f'Unable to open serial port {arduino_data.port}. Please check connection.')
			else:
				ref_to_GraphPage.connectionLbl.configure(text='OPEN', fg='green')
				print(f'Port {arduino_data.port} is now opened')
	elif open_state is False:
		if arduino_data.isOpen() is True:
			try:
				arduino_data.close()
			except:
				messagebox.showerror('Damn !',
									 f'Unable to close serial port {arduino_data.port}. Please check connection.')
			else:
				ref_to_GraphPage.connectionLbl.configure(text='')
				print(f'Port {arduino_data.port} is now closed')
		else:
			messagebox.showinfo('Hey buddy !', 'Serial port already closed.')


def resize_sample(series_name_list_to_resize, sample_size):
	"""
	Resize each array of data according to the sample size value.
	"""
	while len(dict_of_series[series_name_list_to_resize[0]]) > sample_size:
		for serie_name in series_name_list_to_resize:
			dict_of_series[serie_name].pop(0)


def save_data_as_csv(state):
	"""
	Create a new csv file for saving data.
	"""
	global save_data_flg
	if arduino_data.isOpen() is True:
		if state is True and save_data_flg is False:  # Create the file name.
			print("START recording data...")
			config['DATA_FILENAME'] = 'Data_log_{date:%Y-%m-%d_%H-%M-%S}.csv'.format(date=datetime.datetime.now())
			save_data_flg = True
			print(config['DATA_FILENAME'])
		elif state is False and save_data_flg is True:  # Close the csv file and rename it with the actual time code
			# format.
			save_data_flg = False
			data_filename_closed = 'Data_log_{date:%Y-%m-%d_%H-%M-%S}.csv'.format(date=datetime.datetime.now())
			os.rename(config['DATA_FILENAME'], data_filename_closed)
			print("STOP recording data and saving record as csv file.")
			print(data_filename_closed)
	else:
		messagebox.showinfo('Come on buddy...', 'No serial port opened. No data to record!')


def serial_to_array():
	"""
	Listen the serial connection and return an array of data
	"""
	if arduino_data.isOpen() is True:
		while arduino_data.inWaiting() == 0:  # Wait here until there is data
			pass

		arduino_string = arduino_data.readline()  # read the line of text from the serial port
		arduino_string = arduino_string.decode('utf-8')  # Decode the Byte type data to str data.
		# Needed with python 3.4 and later
		data_array = arduino_string.split(',')  # Split it into an array called data_array
		# print(data_array, type(data_array))
		return data_array


def build_parameters_widgets(labels_list):
	"""
	Setup positions of parameters widgets on page "page_name"
	All entry widget are already build ans stored in dict_of_series[<serie>].widget_list
	"""
	print('Setup widgets on param page ...')
	if dict_of_series == {}:
		print('dict_of_series is empty !')
		pass
	else:
		# Build a Label for each parameter name included in labels_list (column header)
		for index, label in enumerate(labels_list):
			tkinter.Label(ref_to_ParamPage, text=label).grid(row=1, column=index)
		serie_row = 2

		# For each serie included in dict_of_series...
		for serie in dict_of_series:
			dict_of_series[serie].build_widgets_list(location=ref_to_ParamPage)
			# ... build a row with the entry widget included in widget_list attribut
			for column_index, serie_widgets in enumerate(dict_of_series[serie].widget_list):
				serie_widgets.grid(row=serie_row, column=column_index, padx=3, pady=5)
			serie_row += 1


def save_graph_parameters(the_dict):
	"""
	Save actual graph parameters to config.otp file.
	! Previous backup is overwritten
	"""
	if dict_of_series != {}:
		if messagebox.askokcancel("Please confirm", "Are you sure you want to save the actual settings ?\n "
												 "(Any previous parameters backup will be overwritten)"):
			for serie in the_dict:
				# my_string = ''
				parameter_list = []
				for parameter_name in SensorSeries.attribut_widget_list:
					parameter_value = the_dict[serie].get_serie_parameters(parameter_name)
					parameter_list.append(parameter_value)
					# my_string = ','.join(parameter_list)
				# print(f"my_string:{# parameter_list}")
				config[serie] = parameter_list
				print(config[serie])
				save_config(config)
		else:
			print("Ok, nothing this time...")
	else:
		messagebox.showinfo("Come on buddy...", "No serie to monitor... no parameters to load...")


def load_graph_parameters():
	"""
	Overwrite actual parameters with values saved
	"""
	if dict_of_series != {}:
		if messagebox.askokcancel("Please confirm", "Are you sure you want to overwrite the actual settings ?"):
			# Update serie's attribut with values of config
			for serie in dict_of_series:
				for attr, value in zip(dict_of_series[serie].attribut_widget_list, config[serie]):
					print(f"attr:{attr} type:{type(attr)} : value:{value} type:{type(value)}")
					setattr(dict_of_series[serie], attr, value)
				# rebuild each entry widget with new values
				dict_of_series[serie].build_widgets_list(location=ref_to_ParamPage)
			print('Done !')
		else:
			print("Ok, nothing this time...")
	else:
		messagebox.showinfo("Come on buddy...", "No serie to monitor... no parameters to load...")


def save_config(dict_to_save):
	"""Save config_dict to a json file"""
	if dict_of_series != {}:
		try:
			with open("config.otp", 'w') as f:
				json.dump(dict_to_save, f)
				print("Configuration saved.")
		except:
			print("Save config failed !")
	else:
		messagebox.showinfo("Come on buddy...", "No serie to monitor... no parameters to save...")


def load_config():
	"""Load config_dict from a json file"""
	global config
	try:
		with open("config.otp", 'r') as f:
			config = json.load(f)

		colors = dict(matplotlib.colors.BASE_COLORS, **matplotlib.colors.CSS4_COLORS)
		for color_name, color_value in colors.items():
			config['available_colors'].append(color_name)
			config['available_colors'].append(color_value)
		print("Configuration loaded.")
	except:
		print("Load config failed !")


def join_series_data(dict_of_series, index):
	"""
	Return a list of all the data of the same index
	Used for saving data as csv file
	"""
	row_data_list = []
	for serie in dict_of_series:
		row_data_list.append(str(dict_of_series[serie].data[index]))
	return row_data_list


def animate(i):
	"""

	"""
	if arduino_data.isOpen() is True:
		global dict_of_series

		if len(dict_of_series) == 0:  # Series are not built yet
			dict_of_series = dict_of_series_init()  # initialize dict_of_series
			# print (f'from animate:{ref_to_ParamPage}')
			build_parameters_widgets(labels_list=SensorSeries.attribut_widget_list)
			print(f"dict_of_series initialized with {len(dict_of_series)} series.")

		while (arduino_data.inWaiting() == 0):
			pass

		raw_values_array = serial_to_array()
		serie_values_list = raw_values_array[1::3]
		series_name_list = raw_values_array[0::3]  # Maybe not the most efficient place to put it...

		for key_name, value in zip(series_name_list, serie_values_list):
			dict_of_series[key_name].append(float(value))

		clear_subplot(array_of_subplot=subplot_array)

		for rank_in_list, subplot in enumerate(subplot_array):
			for index, serie in dict_of_series.items():
				if serie.graph_number - 1 == rank_in_list:
					subplot.set_title(serie.name)
					subplot.set_ylim(serie.ymin, serie.ymax)
					subplot.set_ylabel(serie.ylabel)
					subplot.plot(
						serie.data,
						color=serie.color,
						marker=serie.marker,
						linestyle=serie.line_style,
						linewidth=serie.line_size,
						markersize=serie.marker_size)

		if save_data_flg is True:
			global save_inital_data_flg
			my_file = open(config['DATA_FILENAME'], 'a', newline='')

			if save_inital_data_flg is False:
				try:
					the_writer = csv.writer(my_file, dialect='excel')
					i = 0
					while i < len(dict_of_series[series_name_list[0]].data):
						# print(f' My row of data is :{join_series_data(dict_of_series, i)}')
						the_writer.writerow(join_series_data(dict_of_series, i))
						i += 1
					save_inital_data_flg = True
				finally:
					my_file.close()

			else:
				try:
					the_writer = csv.writer(my_file, dialect='excel')
					# print(f' My row of data is :{join_series_data(dict_of_series, -1)}')
					the_writer.writerow(join_series_data(dict_of_series, -1))
				finally:
					my_file.close()


class SensorSeries:
	"""
	Data and associated parameters of incoming sensor values.
	SensorSeries.sample_size            --> give the current sample size of all series.
	<object>.append                     --> Cast and add values to data array.
	<object>.resize                     --> Resize data array in accordance to the desired sample size
	<object>.build_widgets_list         --> Build a list that contain labels and entries widgets used to change attributs values
	<object>._bind_event_to_entry_widget --> bind a <Return> event to widgets in widget_list

	"""
	sample_size = 50
	parameters_dictionary = {}
	attribut_widget_list = [
		'name',
		'units',
		'ylabel',
		'ymin',
		'ymax',
		'color',
		'marker',
		'line_style',
		'line_size',
		'marker_size',
		'graph_number'
	]
	count = 0
	ENTRY_WIDTH = 12

	def __init__(self, name):
		self.name = name
		self.units = 'units'
		self.ymin = 0
		self.ymax = 100
		self.color = 'b'
		self.marker = 'o'
		self.line_style = '-'
		self.marker_size = 0
		self.line_size = 1
		self.ylabel = 'Y label'
		self.title = name
		self.graph_number = 1
		self.data = []
		self.widget_list = []
		SensorSeries.count += 1

	def __getattr__(self, attr):
		"""
		If the attribut_name does not exist... tell it !
		"""
		# print('\n__getattr__ --> self.__dict__[attr] --->', self.__dict__[attr])
		# return self.__dict__[attr]
		print('Pas glop !')
		print(f'!-->{attribut_name}<--! Does not exist here !')

	# def __getstate__(self):
	# 	print('\n__getstate__ --> self.__dict__ --->', self.__dict__)
	# 	return self.__dict__
	#
	# def __setstate__(self, state):
	# 	print('\n__setstate__ --> state --->', state)
	# 	self.__dict__ = state

	def append(self, value_to_append):
		"""
		Cast and add values to data array.
		"""
		# print(f'value to append -->{value_to_append}<--')
		try:
			self.data.append(float(value_to_append))
		except:
			print(f'Conversion failed ! value --> {value_to_append} <-- not added to {self.name} data.')
		finally:
			if len(self.data) > SensorSeries.sample_size:
				# print('should resize !')
				self.resize(new_sample_size=SensorSeries.sample_size)

	def resize(self, new_sample_size):
		"""
		Resize data array in accordance to the desired new sample size
		"""
		while len(self.data) > new_sample_size:
			# print(f'Resizing serie {self.name}')
			self.data.pop(0)

	def build_widgets_list(self, location):
		"""
		This build a list that contain labels and entry widgets used to change attributs values
		"""
		for index, attr_name in enumerate(SensorSeries.attribut_widget_list):
			if index == 0:
				# the 1st one is a label for the name
				self.widget_list.append(tkinter.Label(location, text=self.name))
			else:
				# All the others are entry widgets
				self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
				self.widget_list[index].delete(0, "end")
				self.widget_list[index].insert(0, getattr(self,attr_name))

		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[1].delete(0, "end")
		# self.widget_list[1].insert(0, self.units)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[2].delete(0, "end")
		# self.widget_list[2].insert(0, self.ylabel)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[3].delete(0, "end")
		# self.widget_list[3].insert(0, self.ymin)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[4].delete(0, "end")
		# self.widget_list[4].insert(0, self.ymax)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[5].delete(0, "end")
		# self.widget_list[5].insert(0, self.color)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[6].delete(0, "end")
		# self.widget_list[6].insert(0, self.marker)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[7].delete(0, "end")
		# self.widget_list[7].insert(0, self.line_style)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[8].delete(0, "end")
		# self.widget_list[8].insert(0, self.line_size)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[9].delete(0, "end")
		# self.widget_list[9].insert(0, self.marker_size)
		# self.widget_list.append(tkinter.Entry(location, width=SensorSeries.ENTRY_WIDTH))
		# self.widget_list[10].delete(0, "end")
		# self.widget_list[10].insert(0, self.graph_number)

		self._bind_event_to_entry_widget(widget_list=self.widget_list)
		# print(self.widget_list)
		self.fill_entry_widgets(widget_list=self.widget_list)
		print(f'Finish to build widgets of serie {self.name}')

	def fill_entry_widgets(self, widget_list):
		for widget, attribut in zip(widget_list, SensorSeries.attribut_widget_list):
			# print(f'-->{widget}<-- :{attribut}')
			SensorSeries.parameters_dictionary_append(
				widget_name=widget,
				attribut_name=attribut)

	def _bind_event_to_entry_widget(self, widget_list):
		"""
		Bind a <FocusOut> event to widgets in widget_list
		"""
		for widget in widget_list:
			try:
				# widget.bind('<Return>', self._on_enter)
				widget.bind('<FocusOut>', self._on_enter)
			except Exception as e:
				raise e

	def _on_enter(self, event):
		"""
		This event update attributs values of the serie
		"""
		test_result, casted_value = value_compliance_check(SensorSeries.parameters_dictionary[event.widget],
														   event.widget.get())
		print(f' Type result:{type(test_result)} ; test_result:{test_result}')
		print(f' Type casted_value:{type(casted_value)} ; casted_value:{casted_value}')

		if test_result is True:
			setattr(self, SensorSeries.parameters_dictionary[event.widget], casted_value)
		else:
			messagebox.showwarning('Warning !', f'{event.widget.get()} is not a valid value !')

	def get_serie_parameters(self, parameter_name):
		return getattr(self, parameter_name)

	def change_sample_size(cls, new_sample_size):
		"""
		Change the sample size value for all series
		"""
		SensorSeries.sample_size = new_sample_size

	change_sample_size = classmethod(change_sample_size)

	def parameters_dictionary_append(cls, widget_name, attribut_name):
		"""
		Append a dictionnary of all widgets name and its associated attribut name.
		"""
		SensorSeries.parameters_dictionary[widget_name] = attribut_name

	parameters_dictionary_append = classmethod(parameters_dictionary_append)


class DataLogApp(tkinter.Tk):
	"""
	Design the main application window and menu bar
	"""

	def __init__(self, *arg, **kwargs):
		tkinter.Tk.__init__(self, *arg, **kwargs)

		tkinter.Tk.wm_title(self, "Analogue Data Acquisition of the poor")

		# create a frame to put the menu in
		container = tkinter.Frame(self)
		container.pack(side='top', fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# create a container named "menu_bar" that will contain all menu items
		menu_bar = tkinter.Menu(container)

		# --- File menu ---
		file_menu = tkinter.Menu(menu_bar, tearoff=0)
		# file_menu.add_command(label="Save settings", command=lambda: save_config(config))
		# file_menu.add_command(label="Load settings", command=lambda: load_config())
		# file_menu.add_separator()
		file_menu.add_command(label="Exit", command=quit)
		menu_bar.add_cascade(label="File", menu=file_menu)

		# --- Record data menu ---
		data_menu = tkinter.Menu(menu_bar, tearoff=1)
		data_menu.add_command(label="Start record", command=lambda: save_data_as_csv(True))
		data_menu.add_command(label="Stop record", command=lambda: save_data_as_csv(False))
		data_menu.add_separator()
		data_menu.add_command(label="Sample size", command=choose_sample_size)
		data_menu.add_command(label="Clear data",
							  command=clear_data)
		menu_bar.add_cascade(label="Data", menu=data_menu)

		# --- Graph menu ---
		graph_menu = tkinter.Menu(menu_bar, tearoff=1)
		graph_menu.add_command(label="Parameters", command=lambda: self.show_frame(ParamPage))
		graph_menu.add_separator()
		graph_menu.add_command(label='Unique', command=lambda: add_subplots_config(111, 111, 111, 111))
		graph_menu.add_command(label='2 side by side', command=lambda: add_subplots_config(121, 121, 122, 122))
		graph_menu.add_command(label='2 stacked', command=lambda: add_subplots_config(211, 211, 212, 212))
		graph_menu.add_command(label='2 top + 1 bottom', command=lambda: add_subplots_config(221, 222, 212, 212))
		graph_menu.add_command(label='1 top + 2 bottom', command=lambda: add_subplots_config(211, 211, 223, 224))
		graph_menu.add_command(label='2 top + 2 bottom',
							   command=lambda: add_subplots_config(221, 222, 223, 224))
		graph_menu.add_command(label='3 stacked', command=lambda: add_subplots_config(311, 312, 313, 313))
		menu_bar.add_cascade(label="Graph", menu=graph_menu)  # add the serial_port_menu element to the menu_bar element

		# --- Serial port communication menu ---
		serial_port_menu = tkinter.Menu(menu_bar, tearoff=1)  # create a Menu element named "serial_port_menu"
		serial_port_menu.add_command(label='Choose port ...',
									 command=choose_port_com)  # add a command button/label labelled "Choose serial port"
		serial_port_menu.add_command(label='Choose baud rate... ',
									 command=choose_baud_rate)  # add a command button/label labelled "Choose baud rate"
		serial_port_menu.add_command(label='Open Serial COM...',
									 command=lambda: open_serial_connection(
										 True))  # add a command button/label labelled "Start listening"
		serial_port_menu.add_command(label='Close Serial COM...',
									 command=lambda: open_serial_connection(
										 False))  # add a command button/label labelled "Start listening"
		menu_bar.add_cascade(label="Serial port",
							 menu=serial_port_menu)  # add the serial_port_menu element to the menu_bar element

		# --- About menu ---
		text_about = """
		More information on the repository...\n
		https://github.com/scarou/ADAotp """
		about_menu = tkinter.Menu(menu_bar, tearoff=0)
		about_menu.add_command(label='About...', command=lambda: messagebox.showinfo('Well...', text_about))
		tkinter.Tk.config(self, menu=menu_bar)
		menu_bar.add_cascade(label="About...", menu=about_menu)

		self.frames = {}

		pages_dictionary = {StartPage, GraphPage, ParamPage}  # Dictionnary of classes

		for page in pages_dictionary:  # Unpack pages_dictionary with all classes contained
			# print(f'page type:{type(page)} ; page value:{page}')

			frame = page(container, self)  # create an object from each class (frame is now an object)
			# print(f'frame type:{type(frame)} ; frame value:{frame}')

			self.frames[page] = frame  # fill the frames dictionnary with all created objects (pages)
			frame.grid(row=0, column=0, sticky="nsew")  # display all created objects (pages)
		self.show_frame(StartPage)

		global ref_to_ParamPage
		global ref_to_GraphPage
		ref_to_ParamPage = self.frames[ParamPage]
		ref_to_GraphPage = self.frames[GraphPage]

	# print (ref_to_ParamPage)

	def show_frame(self, cont):  # show_frame is a method of DataLogApp
		frame = self.frames[cont]
		frame.tkraise()


class StartPage(tkinter.Frame):
	"""
	Create the Start page
	"""

	def __init__(self, parent, controller):
		"""Build a centered frame, put a label and 2 buttons in it for the Start page"""
		tkinter.Frame.__init__(self,
							   parent)  # Call initialisation of the mother class tkinter.Frame and transmit the parent name
		main_frame = tkinter.Frame(self)
		main_frame.place(anchor='center', relx=.50, rely=.30)

		label = tkinter.Label(main_frame, text="""\nADAotp\n
		\nAnalogue Data Acquisition of the poor\n
		\n (Python 3.6)\n""", font=config['LARGE_FONT'])
		label.grid(row=0, column=0, columnspan=5, pady=10, padx=10)

		button1 = tkinter.Button(main_frame, text="Continue", width=20, command=lambda: controller.show_frame(GraphPage))
		button1.grid(row=1, column=1)
		button2 = tkinter.Button(main_frame, text="Quit", width=20, command=quit)
		button2.grid(row=1, column=3)


class ParamPage(tkinter.Frame):
	"""
	Create the parameters page
	"""
	LABEL_WIDTH = 12

	def __init__(self, parent, controller):
		tkinter.Frame.__init__(self,
							   parent)  # Call initialisation of the mother class tkinter.Frame and transmit the parent name

		parameters_label = tkinter.Label(self, text="\nParameters\n", font=config['LARGE_FONT'])
		parameters_label.grid(row=0, column=0, pady=10, padx=10)

		button_ok = tkinter.Button(self, text="Ok", width=ParamPage.LABEL_WIDTH,
								   command=lambda: controller.show_frame(GraphPage))
		button_ok.grid(row=0, column=1)
		button_save = tkinter.Button(self, text="Save parameters", width=ParamPage.LABEL_WIDTH,
									 command=lambda: save_graph_parameters(dict_of_series))
		button_save.grid(row=0, column=2)
		button_load = tkinter.Button(self, text="Load parameters", width=ParamPage.LABEL_WIDTH,
									 command=load_graph_parameters)
		button_load.grid(row=0, column=3)


class GraphPage(tkinter.Frame):
	"""
	Create the graph monitoring page.
	"""

	def __init__(self, parent, controller):
		# Call initialisation of the mother class tkinter.Frame and transmit the parent name
		tkinter.Frame.__init__(self, parent)

		self.rowconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)

		tkinter.Label(self, text='ADAotp Monitoring Page', font=("Verdana", 14),
					  padx=10, pady=15).grid(row=0, column=3, rowspan=2)

		self.record_data_Label = tkinter.Label(self, text='Record data as .csv', font=("Verdana", 12))
		self.start_button = tkinter.Button(self, text='START', padx=10, pady=5, command=self.start_button_click)
		self.stop_button = tkinter.Button(self, text='STOP', background="red", relief="sunken", padx=10, pady=5,
										  command=self.stop_button_click)

		self.serial_label = tkinter.Label(self, text='Serial', font=("Verdana", 12))
		self.port_com_label = tkinter.Label(self, text=config['port_COM'], width=6, pady=5)
		self.baud_rate_label = tkinter.Label(self, text=config['baud_rate'], width=6, pady=5)
		self.connectionLbl = tkinter.Label(self, text = '', width=6, pady =5)

		self.record_data_Label.grid(row=0, column=0, columnspan=3)
		self.serial_label.grid(row=0, column=4, columnspan=3)
		self.start_button.grid(row=1, column=1)
		self.stop_button.grid(row=1, column=2)
		self.port_com_label.grid(row=1, column=4, sticky='e')
		self.baud_rate_label.grid(row=1, column=5)
		self.connectionLbl.grid(row=1, column=6)

		# création d'un widget 'Canvas' pour l'affichage des graphiques :
		self.canvas = FigureCanvasTkAgg(fig, self)
		self.canvas.draw

		self.canvas.get_tk_widget().grid(row=2, column=0)

		# self.toolbar_frame = tkinter.Frame(self)
		# self.toolbar_frame.grid(row=2,column=0,sticky='w')

		# Doit être mis dans une frame et la frame placée par .grid sinon confli avec
		# méthode .pack automatiquement appelée par NavigationToolbar2TkAgg

		# self.toolbar = NavigationToolbar2TkAgg(self.toolbar_frame, self)
		# self.toolbar.update()

		self.canvas._tkcanvas.grid(row=2, column=0, columnspan=7, padx=5, pady=5, sticky='nswe')



	def start_button_click(self):
		if arduino_data.isOpen() is True:
			self.start_button.configure(background='green', relief='sunken')
			self.stop_button.configure(background='SystemButtonFace', relief='raised')
			save_data_as_csv(True)
		else:
			# popupmsg('No serial port opened. No data to record!')
			messagebox.showinfo('Come on buddy...', 'No serial port opened. No data to record!')

	def stop_button_click(self):
		self.start_button.configure(background='SystemButtonFace', relief='raised')
		self.stop_button.configure(background='red', relief='sunken')
		save_data_as_csv(state=False)


load_config()
app = DataLogApp()  # Create an instance of DataLogApp

# center app window
screen_x = app.winfo_screenwidth()
screen_y = app.winfo_screenheight()
window_x = 1280
window_y = 720
posX = (screen_x // 2) - (window_x // 2)
posY = (screen_y // 2) - (window_y // 2)
geo = f"{window_x}x{window_y}+{posX}+{posY}"
app.geometry(geo)

ani = animation.FuncAnimation(fig, animate, interval=500)

app.mainloop()
