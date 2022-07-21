from tkinter import *
import tkinter as tk
import tkinter
from PIL import Image,ImageTk
from tkinter.ttk import Frame, Label, Style
from tkvideo import tkvideo
from ffpyplayer.player import MediaPlayer
import imageio
import tkinter.font as font
import PIL
from Video_Capture import VideoCapture


class GUI_App:
    def __init__(self, window, window_title):
        self.window = window
        self.window_title = window_title
        self.video_capture = VideoCapture()
        self.window.title(window_title)
        

        self.canvas = tkinter.Canvas(window, width=800, height=600)
        self.canvas.pack(expand=YES, fill=BOTH)

        self.btn_text = tk.StringVar()
        self.btn_text.set("Start")
        self.button_font = font.Font(size=10, weight="bold")
        self.start_btn = tkinter.Button(window, textvariable=self.btn_text, height=5, width=50, command=self.Start_Button_Method, bg="green", fg="white")
        self.start_btn['font'] = self.button_font
        self.start_btn.pack(anchor=tkinter.CENTER, expand=True, pady=10)

        self.delay = 15
        self.Update()

        self.window.mainloop()

    def Update(self):
        ret, frame = self.video_capture.Get_Frames()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(75, 20, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.Update)
    
    def Start_Button_Method(self):
        self.video_capture.play_allowed = not self.video_capture.play_allowed
        if(self.video_capture.play_allowed):
            self.btn_text.set("Stop")
            self.start_btn['bg'] = "red"
        else:
            self.btn_text.set("Start")
            self.start_btn['bg'] = "green"
        print(self.video_capture.play_allowed)


GUI_App(tkinter.Tk(), "Computer-Aided Smart Advertisements (CASA)")