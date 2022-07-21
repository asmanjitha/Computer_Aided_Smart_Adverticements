from Video_Capture import VideoCapture

def load_adverticements():
    male_5_10 = "./Assets/5_10_male.mp4"
    female_5_10 = "./Assets/5_10_female.mp4"
    male_10_15 = "./Assets/10_15_male.mp4"
    female_10_15 = "./Assets/5_10_female.mp4"
    male_20_30 = "./Assets/20_30_male.mp4"
    female_20_30 = "./Assets/20_30_female.mp4"


def CASA_main():
    print("Running")


if __name__ == "__main__":   
    vid = VideoCapture()
    vid.run_video_capture()     
    CASA_main()