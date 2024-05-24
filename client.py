import datetime as dt
import socket
import json
from tkinter import *
from tkinter import ttk
import webbrowser

def select(event):
    selected_indices=list_box.curselection()
    # print(selected_indices)
    url = list_box.get(selected_indices).split('\n')[1]
    webbrowser.open_new(url)

root = Tk()
root.title("Weather & news aggregator")
root.geometry("1000x500+300+200")
root.configure(bg="#3399ff")
root.resizable(False, False)

def search_button_pressed():
    update_weather()
    update_news()
    update_time()

def get_current_time(location):
    # Fetch the current time based on the location
    # You can use pytz or other libraries to handle time zones
    # This is just a placeholder function
    current_time = dt.datetime.now().strftime('%I:%M:%S %p')
    return current_time

search_img = PhotoImage(file="Rounded Rectangle 3.png")
search_box = Label(image=search_img, bg="#3399ff")
search_box.place(x=5, y=10)

search_textfield = Entry(root, justify="left", width=17, font=("poppins", 25, 'bold'), bg="#203243", fg="white", highlightbackground="#203243", border=0)
search_textfield.place(x=30, y=15)
search_textfield.focus()

search_icon = PhotoImage(file="17.png")
img_icon = Button(image=search_icon, borderwidth=0, cursor='hand2', bg="#203243", highlightbackground="#203243", command=search_button_pressed)
img_icon.place(x=370, y=15)

logo = PhotoImage(file="logo.png")
logoo = Label(image=logo, bg="#3399ff")
logoo.place(x=0, y=100)

news_label = Label(root, text="News Articles", font=("Helvetica", 20, "bold"), fg="#ffd73f", bg="#3399ff")
news_label.place(x=705, y=30)

# List box with scroll bar
list_box = Listbox(root, width=43, height=21, font=("Helvetica", 12), bg="#203243", highlightbackground="#203243", fg="white")
list_box.place(x=585, y=70)
list_box.bind('<<ListboxSelect>>', select)

# Add horizontal scrollbar to list box
xscrollbar = ttk.Scrollbar(root, orient=HORIZONTAL, command=list_box.xview)
xscrollbar.place(x=585, y=475, width=390)
list_box.config(xscrollcommand=xscrollbar.set)

# Add vertical scrollbar to list box
scrollbar = ttk.Scrollbar(root, command=list_box.yview)
scrollbar.place(x=980, y=70, height=400)
list_box.config(yscrollcommand=scrollbar.set)

content_frame = PhotoImage(file="bg.png")
Content_frame = Label(image=content_frame, bg="#3399ff")
Content_frame.place(x=0, y=345)
content_frame1 = PhotoImage(file="bg.png")
Content_frame1 = Label(image=content_frame1, bg="#3399ff")
Content_frame1.place(x=0, y=380)

Wind_label = Label(root, text="Wind", font=("Helvetica", 15, "bold"), fg="#203243", bg="#3b82f6")
Wind_label.place(x=10, y=350)

# Weather parameter label
weather_parameter = StringVar()
weather_parameter_label = Label(root, textvariable=weather_parameter, font=("Helvetica", 65, "bold"), fg="white", bg="#3399ff")
weather_parameter_label.place(x=250, y=150)

# time parameter label
time_parameter = StringVar()
time_parameter_label = Label(root, textvariable=time_parameter, font=("Helvetica", 20), fg="#203243", bg="#3399ff")
time_parameter_label.place(x=300, y=250)

# Wind parameter label
wind_parameter = StringVar()
wind_parameter_label = Label(root, textvariable=wind_parameter, font=("Helvetica", 12), fg="#203243", bg="#3b82f6")
wind_parameter_label.place(x=10, y=400)

Humidity_label = Label(root, text="Humidity", font=("Helvetica", 15, "bold"), fg="#203243", bg="#3b82f6")
Humidity_label.place(x=120, y=350)

# Humidity parameter label
humid_parameter = StringVar()
humid_parameter_label = Label(root, textvariable=humid_parameter, font=("Helvetica", 12), fg="#203243", bg="#3b82f6")
humid_parameter_label.place(x=120, y=400)

Description_label = Label(root, text="Description", font=("Helvetica", 15, "bold"), fg="#203243", bg="#3b82f6")
Description_label.place(x=270, y=350)

# Description parameter label
desc_parameter = StringVar()
desc_parameter_label = Label(root, textvariable=desc_parameter, font=("Helvetica", 12), fg="#203243", bg="#3b82f6")
desc_parameter_label.place(x=270, y=400)

Pressure_label = Label(root, text="Pressure", font=("Helvetica", 15, "bold"), fg="#203243", bg="#3b82f6")
Pressure_label.place(x=430, y=350)

# Pressure parameter label
press_parameter = StringVar()
press_parameter_label = Label(root, textvariable=press_parameter, font=("Helvetica", 12), fg="#203243", bg="#3b82f6")
press_parameter_label.place(x=430, y=400)

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def update_weather():
    city = search_textfield.get()

    # Send city information to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        message = f"{city}|weather".encode()
        s.sendall(message)
        data = s.recv(1024)

    # Parse and update weather information
    data_dict = json.loads(data.decode())
    weather_parameter.set(data_dict.get('temperature', 'N/A') + "°C")
    wind_parameter.set(data_dict.get('wind_speed', 'N/A') + " m/s")
    humid_parameter.set(data_dict.get('humidity', 'N/A') + "%")
    desc_parameter.set(data_dict.get('description', 'N/A'))
    press_parameter.set(data_dict.get('pressure', 'N/A') + " hPa")

def update_news():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        message = b'|news'
        s.sendall(message)
        data = s.recv(5120)

    try:
        articles = json.loads(data.decode())

        # Clear the list box
        list_box.delete(0, END)

        for article in articles:
            title = article.get('title', 'N/A')
            link = article.get('link', 'N/A')
            # points = article.get('points', 'N/A')

            # Add the article to the list box
            list_box.insert(END, f"{title}\n{link}\n")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Received data: {data}")

def update_time():
    city = search_textfield.get()

    # Send city information to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        message = f"{city}|time".encode()
        s.sendall(message)
        data = s.recv(1024)

    # Update the time parameter label
    time_parameter.set(data.decode()[1:-1])

root.mainloop()
