import os
import cv2
from ffpyplayer.player import MediaPlayer


class AdvertisementHandler:
    def __init__(self) :
        self.male_5_10 = "./Assets/5_10_male.mp4"
        self.female_5_10 = "./Assets/5_10_female.mp4"
        self.male_10_15 = "./Assets/10_15_male.mp4"
        self.female_10_15 = "./Assets/5_10_female.mp4"
        self.male_20_30 = "./Assets/20_30_male.mp4"
        self.female_20_30 = "./Assets/20_30_female.mp4"

        self.playing = False
        self.currentConfidence = ""
        self.prevConfidence = []
        self.cap = None
    
    def play(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        player = MediaPlayer(video_path)
        if (self.cap.isOpened()== False):
            print("Error opening video stream or file")
        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            audio_frame, val = player.get_frame()
            if ret == True:
                cv2.imshow('Frame',frame)

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
                if val != 'eof' and audio_frame is not None:
                    #audio
                    img, t = audio_frame
            else:
                break
        self.cap.release()
        cv2.destroyAllWindows()
    
    def play_advertisement(self, confidence):
        if(not self.playing):
            self.playing = True
            self.currentConfidence = confidence
            self.prevConfidence = []
            video_path = "./Assets/" + confidence + ".mp4"
            self.play(video_path)
            self.playing = False

        # if(self.playing):
        #     if(len(self.prevConfidence) >= 2):
        #         self.prevConfidence.pop(0)
        #     self.prevConfidence.append(confidence)
        #     if(len(self.prevConfidence) == 2 and self.prevConfidence[0] == self.prevConfidence[1] and self.prevConfidence[0] != "default" and self.currentConfidence != "default"):
        #         self.playing = False
        #         print("Changing adverticement...")
        #         self.cap.release()
        #         while(self.cap.isOpened()):
        #             continue
        #         video_path = "./Assets/" + confidence + ".mp4"
        #         self.currentConfidence = confidence
        #         self.play(video_path)









