import cv2
import math
import time
import argparse
import sched
import threading
import argparse
from collections import Counter
from Advertisement_Handler import AdvertisementHandler
import operator

class VideoCapture:

    def __init__(self) :
        self.faceProto = "./Model_Files/opencv_face_detector.pbtxt"
        self.faceModel = "./Model_Files/opencv_face_detector_uint8.pb"

        self.ageProto = "./Model_Files/age_deploy.prototxt"
        self.ageModel = "./Model_Files/age_model.h5"

        self.genderProto = "./Model_Files/gender_deploy.prototxt"
        self.genderModel = "./Model_Files/gender_model.h5"

        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.genderList = ['Male', 'Female']

        self.ageNet = cv2.dnn.readNet(self.ageModel,self.ageProto)
        self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)
        self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source")

        self.padding = 20

        self.s = sched.scheduler(time.time, time.sleep)

        self.confidence_list = []
        self.advertisementHandler = AdvertisementHandler()
        self.running_thread = threading.Thread(target=self.thread_function, daemon=True)
        self.running_thread.start()

        self.play_allowed = False

    def insert_confidence(self, confidence):
        if(len(self.confidence_list) >= 150):
            self.confidence_list.pop(0)
        if(len(confidence) == 2):
            if(confidence[0] == self.genderList[0]):
                if(confidence[1] == self.ageList[0] or confidence[1] == self.ageList[1] or confidence[1] == self.ageList[2]):
                    conf = "male_5_10"
                elif(confidence[1] == self.ageList[3]):
                    conf = "male_10_15"
                else:
                    conf = "male_20_30"
            elif(confidence[0] == self.genderList[1]):
                if(confidence[1] == self.ageList[0] or confidence[1] == self.ageList[1] or confidence[1] == self.ageList[2]):
                    conf = "female_5_10"
                elif(confidence[1] == self.ageList[3]):
                    conf = "female_10_15"
                else:
                    conf = "female_20_30"
        else:
            conf = "default"
        self.confidence_list.append(conf)

    # def pick_advertisement(self, sc): 
    #     c = Counter(self.confidence_list)
    #     c = dict(c)
    #     max_key = max(c, key=c.get)
    #     print(max_key)
    #     print("Picking advertisement...")
    #     playThread = threading.Thread(target=self.advertisementHandler.play_advertisement, args=(max_key, ),  daemon=True)
    #     playThread.start()

    #     self.s.enter(10, 1, self.pick_advertisement, (sc,))

    def pick_advertisement(self, sc): 
        print("Picking advertisement...", self.play_allowed)
        if(self.play_allowed):
            c = Counter(self.confidence_list)
            c = dict(c)
            max_key = max(c, key=c.get)
            print(max_key)
            playThread = threading.Thread(target=self.advertisementHandler.play_advertisement, args=(max_key, ),  daemon=True)
            playThread.start()
        self.s.enter(10, 1, self.pick_advertisement, (sc,))

    def getFaceBox(self, net, frame,conf_threshold = 0.75):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn,1.0,(300,300),[104, 117, 123], True, False)

        net.setInput(blob)
        detections = net.forward()
        bboxes = []

        for i in range(detections.shape[2]):
            confidence = detections[0,0,i,2]
            if confidence > conf_threshold:
                x1 = int(detections[0,0,i,3]* frameWidth)
                y1 = int(detections[0,0,i,4]* frameHeight)
                x2 = int(detections[0,0,i,5]* frameWidth)
                y2 = int(detections[0,0,i,6]* frameHeight)
                bboxes.append([x1,y1,x2,y2])
                cv2.rectangle(frameOpencvDnn,(x1,y1),(x2,y2),(0,255,0),int(round(frameHeight/150)),8)

        return frameOpencvDnn , bboxes
    
    def thread_function(self):
        self.s.enter(5, 1, self.pick_advertisement, (self.s,))
        self.s.run()
    

    def run_video_capture(self):
        # x = threading.Thread(target=self.thread_function, daemon=True)
        # x.start()

        while cv2.waitKey(1) < 0:
            #read frame
            t = time.time()
            hasFrame , frame = self.cap.read()

            if not hasFrame:
                cv2.waitKey()
                break
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            #creating a smaller frame for better optimization
            # small_frame = cv2.resize(frame,(0,0),fx = 0.5,fy = 0.5)
            small_frame = cv2.resize(frame,(0,0),fx = 1,fy = 1)

            frameFace ,bboxes = self.getFaceBox(self.faceNet,small_frame)
            if not bboxes:
                cv2.imshow("Age Gender Demo", small_frame)
                confidence = []
                # print(confidence)
                self.insert_confidence(confidence)
                continue
            for bbox in bboxes:
                face = small_frame[max(0,bbox[1]-self.padding):min(bbox[3]+self.padding,frame.shape[0]-1),
                        max(0,bbox[0]-self.padding):min(bbox[2]+self.padding, frame.shape[1]-1)]
                
                try:
                    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
                except Exception as e:
                    print(str(e))
                    
                self.genderNet.setInput(blob)
                genderPreds = self.genderNet.forward()
                gender = self.genderList[genderPreds[0].argmax()]
                # print("Gender : {}, conf = {:.3f}".format(gender, genderPreds[0].max()))

                self.ageNet.setInput(blob)
                agePreds = self.ageNet.forward()
                age = self.ageList[agePreds[0].argmax()]
                # print("Age Output : {}".format(agePreds))
                # print("Age : {}, conf = {:.3f}".format(age, agePreds[0].max()))

                confidence = [gender, age]

                label = "{},{}".format(gender, age)
                cv2.putText(frameFace, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow("Age Gender Demo", frameFace)

                # print(confidence)
                self.insert_confidence(confidence)

        # After the loop release the cap object
        self.cap.release()
        # Destroy all the windows
        cv2.destroyAllWindows()

    def Get_Frames(self):
        if self.cap.isOpened():

            hasFrame , frame = self.cap.read()

            if not hasFrame:
                return (hasFrame, None)

            else:
                small_frame = cv2.resize(frame,(0,0),fx = 1,fy = 1)
                frameFace ,bboxes = self.getFaceBox(self.faceNet,small_frame)

                if not bboxes:
                    # cv2.imshow("Age Gender Demo", small_frame)
                    confidence = []
                    # print(confidence)
                    self.insert_confidence(confidence)
                    return (hasFrame, small_frame)
                else:
                    for bbox in bboxes:
                        face = small_frame[max(0,bbox[1]-self.padding):min(bbox[3]+self.padding,frame.shape[0]-1),
                                max(0,bbox[0]-self.padding):min(bbox[2]+self.padding, frame.shape[1]-1)]
                        
                        try:
                            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
                            self.genderNet.setInput(blob)
                            self.ageNet.setInput(blob)
                        except Exception as e:
                            print(str(e))
                            
                        # self.genderNet.setInput(blob)
                        genderPreds = self.genderNet.forward()
                        gender = self.genderList[genderPreds[0].argmax()]
                        # print("Gender : {}, conf = {:.3f}".format(gender, genderPreds[0].max()))

                        # self.ageNet.setInput(blob)
                        agePreds = self.ageNet.forward()
                        age = self.ageList[agePreds[0].argmax()]
                        # print("Age Output : {}".format(agePreds))
                        # print("Age : {}, conf = {:.3f}".format(age, agePreds[0].max()))

                        confidence = [gender, age]

                        label = "{},{}".format(gender, age)
                        finalFrame = cv2.putText(frameFace, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                        # cv2.imshow("Age Gender Demo", frameFace)

                        # print(confidence)
                        self.insert_confidence(confidence)
                        return (hasFrame, finalFrame)



        else:
            return (False, None)


    def __delattr__(self) :
        self.cap.release()
        cv2.destroyAllWindows()
