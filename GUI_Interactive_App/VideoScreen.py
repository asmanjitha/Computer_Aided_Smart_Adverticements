import tkinter as tk
import vlc

class Screen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg = 'black')
        self.settings = { # Inizialazing dictionary settings
            "width" : 1024,
            "height" : 576
        }
        self.settings.update(kwargs) # Changing the default settings
        # Open the video source |temporary
        self.video_source =  "./Assets/male_5_10.mp4"

        # Canvas where to draw video output
        self.canvas = tk.Canvas(self, width = self.settings['width'], height = self.settings['height'], bg = "black", highlightthickness = 0)
        self.canvas.pack()

        # Creating VLC player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()


    def GetHandle(self):
        # Getting frame ID
        return self.winfo_id()

    def play(self, _source):
        # Function to start player from given source
        Media = self.instance.media_new(_source)
        Media.get_mrl()
        self.player.set_media(Media)

        #self.player.play()
        self.player.set_hwnd(self.GetHandle())
        self.player.play()