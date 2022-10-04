from tkinter import *
from PIL import ImageTk,Image
import mysql.connector #Import the MYSQL module
import paho.mqtt.client as paho
from tkinter import ttk #For the drop menu usage
import glob
import csv
import os
import configparser



root = Tk()
root.title('Read CVS and Send Over MQTT')
root.geometry("560x430") #Define the gemoetry of the window


######################################BACKEND######################################

#Read the Ini File
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
config_obj = configparser.ConfigParser()
config_obj.read(os.path.join(path, 'config.ini'))
cfpath = config_obj["PATH"]
cfMQTT = config_obj["MQTT"]
cfTOPIC = config_obj["TOPIC"]

#Setting the parameters
filepath = cfpath["dir"]
ipadd = cfMQTT["ip"]
par_cell = cfTOPIC['cell']
par_bonggap = cfTOPIC['bondg']
par_pass = cfTOPIC['pass']
par_barcode = cfTOPIC['barcode']


#Read the CSV


def checkP():
	global filepath
	global frame_center
	global frame_right
	global frame_left
	global C1
	global C2
	global C3
	global Folder_label
	global oval3
	global oval2
	global oval1
	client = paho.Client()
	fil = glob.glob(filepath + "/*.csv")
	try:
		isExist = os.path.exists(filepath)
		if isExist:
				try:
					File = open(fil[0])
				except Exception as e:
					frame_center.destroy()
					C3.destroy()
					Folder_label.destroy()
#					oval3.destroy()
					frame_center = LabelFrame(root,text="Folder",height=50,width=150,labelanchor='n')
					frame_center.grid(row=0,column=2,pady=5,padx=5)
					frame_center.grid_propagate(0)
					C3 = Canvas(frame_center,height=20,width=20)  # Create 200x200 Canvas widget
					C3.grid(row=0,column=0)
					Folder_label = Label(frame_center, text="Waiting on file")  # Set the LAbel widget
					Folder_label.grid(row=0,column=1)
					oval3 = C3.create_oval(10, 10, 20, 20, fill="green")
				else:
					frame_center.destroy()
					C3.destroy()
					Folder_label.destroy()
#					oval3.destroy()
					frame_center = LabelFrame(root,text="Folder",height=50,width=150,labelanchor='n')
					frame_center.grid(row=0,column=2,pady=5,padx=5)
					frame_center.grid_propagate(0)
					C3 = Canvas(frame_center,height=20,width=20)  # Create 200x200 Canvas widget
					C3.grid(row=0,column=0)
					Folder_label = Label(frame_center, text="File Read")  # Set the LAbel widget
					Folder_label.grid(row=0,column=1)
					oval3 = C3.create_oval(10, 10, 20, 20, fill="blue")	
					Reader = csv.reader(File)
					Data = list(Reader)
					cells_number = []
					for x in list(range(1, len(Data))):
						cells_number.append(Data[x][0])
					cell_str=",".join(str(x) for x in cells_number)
					bondgap = []
					for x in list(range(1, len(Data))):
						bondgap.append(Data[x][6])
					bond_str=",".join(str(x) for x in bondgap)
					passorf = []
					for x in list(range(1, len(Data))):
						passorf.append(Data[x][7])
					pass_str=",".join(str(x) for x in passorf)
					try:
						client.connect(ipadd, 1883, 60)
					except Exception as e:
						global Data_label
						Data_label.destroy()
						Data_label = Label(frame_right, text="Broker Down")  # Set the LAbel widget
						Data_label.grid(row=0,column=1)
						C2.itemconfig(oval2, fill="red")

					else:
						client.publish(par_cell,cell_str)
						client.publish(par_bonggap,bond_str)
						client.publish(par_pass,pass_str)
						client.disconnect()
						listbox.insert(0,"File Read:" + " " + fil[0])
						os.remove(fil[0])
		else:
			frame_center.destroy()
			C3.destroy()
			Folder_label.destroy()
#			oval3.destroy()
			frame_center = LabelFrame(root,text="Folder",height=50,width=150,labelanchor='n')
			frame_center.grid(row=0,column=2,pady=5,padx=5)
			frame_center.grid_propagate(0)
			C3 = Canvas(frame_center,height=20,width=20)  # Create 200x200 Canvas widget
			C3.grid(row=0,column=0)
			Folder_label = Label(frame_center, text="Disconnected")  # Set the LAbel widget
			Folder_label.grid(row=0,column=1)
			oval3 = C3.create_oval(10, 10, 20, 20, fill="red")

	finally:
		root.after(5000,checkP)


def on_connect(client, userdata, flags, rc):
	if rc==0:
		client.connected_flag=True #set flag
		client.subscribe(par_barcode,qos=0) 
		client.loop_start()
	else:
		print("Bad connection Returned code=",rc)

def on_message(client, userdata, message):
		global Data_label
		global Status_label
		msg = str(message.payload.decode("utf-8"))

		if "400" in msg:
			Data_label.destroy()
			Status_label.destroy()
			Data_label = Label(frame_right, text="Message Send")  # Set the LAbel widget
			Data_label.grid(row=0,column=1)
			C2.itemconfig(oval2, fill="green")
			listbox.insert(0,"Barcode Receive:" + " " + msg)
			Status_label = Label(frame_left, text="System Running")  # Set the LAbel widget
			Status_label.grid(row=0,column=1)
			C1.itemconfig(oval2, fill="green")
		elif msg == "Fail":
			Data_label.destroy()
			Data_label = Label(frame_right, text="Message Fail")  # Set the LAbel widget
			Data_label.grid(row=0,column=1)
			C2.itemconfig(oval2, fill="red")
			listbox.insert(0,"Barcode Fail to be receive")

client = paho.Client()
client.on_connect=on_connect
client.on_message=on_message #attach function to callback
client.connect(ipadd, 1883, 60) #connect to broker
client.subscribe(par_barcode,qos=0) 
client.loop_start()


#########################################FRONTEND##################################


#Create the menu
main_menu = Menu(root)
root.config(menu=main_menu)

#create a menu item

file_menu = Menu(main_menu)
main_menu.add_cascade(label="File", menu=file_menu)
#file_menu.add_command(label="Database", command=open_database)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)


frame_left = LabelFrame(root,text="Status",height=50,width=150,labelanchor='n')
frame_left.grid(row=0,column=0,pady=5,padx=5)
frame_left.grid_propagate(0)
frame_right = LabelFrame(root,text="MQTT Message",height=50,width=150,labelanchor='n')
frame_right.grid(row=0,column=1,pady=5,padx=5)
frame_right.grid_propagate(0)
frame_center = LabelFrame(root,text="Folder",height=50,width=150,labelanchor='n')
frame_center.grid(row=0,column=2,pady=5,padx=5)
frame_center.grid_propagate(0)




C1 = Canvas(frame_left,height=20,width=20)  # Create 200x200 Canvas widget
C1.grid(row=0,column=0)
Status_label = Label(frame_left, text="Unknow")  # Set the LAbel widget
Status_label.grid(row=0,column=1)

oval1 = C1.create_oval(10, 10, 20, 20, fill="grey")  # Create a circle on the Canvas


C2 = Canvas(frame_right,height=20,width=20)  # Create 200x200 Canvas widget
C2.grid(row=0,column=0)
Data_label = Label(frame_right, text="Unknow")  # Set the LAbel widget
Data_label.grid(row=0,column=1)

oval2 = C2.create_oval(10, 10, 20, 20, fill="grey")  # Create a circle on the Canvas


C3 = Canvas(frame_center,height=20,width=20)  # Create 200x200 Canvas widget
C3.grid(row=0,column=0)
Folder_label = Label(frame_center, text="Unknow")  # Set the LAbel widget
Folder_label.grid(row=0,column=1)

oval3 = C3.create_oval(10, 10, 20, 20, fill="grey")  # Create a circle on the Canvas


#create the list box


listbox = Listbox(root,height=20,width=60)
listbox.grid(row=2,column=0, columnspan=3,pady=10,padx=10)

#Button to check

# my_button = Button(root, text="CHECK", command=checkMQTT)  # Set a "Start button". The "start_indicators" function is a call-back.
# my_button.grid(row=0,column=4)



root.after(5000,checkP)
root.mainloop()