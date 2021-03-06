import os
import cv2
import time
import numpy as np
from datetime import datetime
from threading import Thread, Lock
from ..no_flask_email import send_email
from ..models import VideoFile, Alert, Camera

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

rec = None
engine = create_engine('postgres://testuser:test@127.0.0.1/test')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

#gst-launch-1.0 v4l2src ! video/x-raw,width=640,height=480 ! videoscale ! theoraenc ! oggmux ! shout2send ip=127.0.0.1 port=8000 password=hackme mount=/test.ogv
class CameraRecoder(Thread):
    def __init__(self, camera, fps=20, file_duration=60, min_area=1000):
        Thread.__init__(self)
        self.on = True
        self.name = camera.name
        self.id =camera.id
        self.email = camera.owner_id
        self.link = camera.link
        self.capture = cv2.VideoCapture(camera.link)
        self.subtractor = cv2.BackgroundSubtractorMOG()
        self.frame = None
        self.last_frame = None
        self.directory = 'app/static/capture/'+ str(camera.id) +'/'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)



        self.path = self.directory + str(datetime.now().strftime('%s'))+'.ogg'
        self.codec = cv2.cv.CV_FOURCC('T','H','E','O')
        self.fps = fps
        self.size = (camera.width, camera.height)
        self.out = cv2.VideoWriter(self.path, self.codec, fps, self.size)
        self.last_detection = datetime(2010,1,1)

        self.file_duration = file_duration
        self.min_area = min_area
        self.cap_start_time = datetime.now()

    def detect_motion(self):
        now = datetime.now()
        if (now - self.last_detection).seconds < 60:
            return False

        # if self.last_frame is None:
        #     return False
        if self.frame is None:
            return False

        thresh = self.subtractor.apply(self.frame, learningRate=0.01)

        # gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        # result = cv2.absdiff(gray, self.last_frame)
        # _,thresh = cv2.threshold(result, 125, 255, cv2.THRESH_BINARY)

        # cv2.imshow('tres', thresh)

        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        ret = False;
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                self.last_detection = datetime.now()
                cv2.drawContours(self.frame, contour, -1, (0,255,0), 3)
                ret = True
        cv2.imshow(str(self.id), self.frame)
        cv2.waitKey(10)
        return ret

    def save_video(self):
        #save frame
        self.out.write(self.frame)
        #Check the duration
        now = datetime.now()
        elaps = now - self.cap_start_time
        if elaps.seconds > self.file_duration:
            #save video
            self.out.release()
            record = VideoFile(src=self.id,
                               path=self.path,
                               start_time = self.cap_start_time,
                               end_time = now)
            db_session.add(record)
            #Start new file
            self.cap_start_time = datetime.now()
            self.path = self.directory+self.cap_start_time.strftime('%s')+'.ogg'
            self.out = cv2.VideoWriter(self.path, self.codec, self.fps, self.size)
            db_session.commit()


    def run(self):
        while self.on:
            # try:
            if self.frame is not None:
                self.last_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            ret, self.frame = self.capture.read()

            if not ret:
                continue

            self.save_video()
            if self.detect_motion():
                alert = Alert(camera = self.id,
                              video = self.path,
                              time = datetime.now()
                              )
                db_session.add(alert)
                db_session.commit()

                # cv2.imshow(str(self.id), self.frame)
                # cv2.waitKey(10)
            # except:
            #     continue
            # email = self.email
            # if email:
            #     send_email(self.email, '[CamDroid] Alert ', 'Momvement detected at ' + self.name)

    def remove_camera(self):
        self.on = False


class RecordManager(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.cameras = dict()
        self.cameras_lock = Lock()


    def add_camera(self, camera):
        ''' Add a camera to the processing queue '''
        self.cameras_lock.acquire()

        if self.cameras.get(camera.id, None) is None:
            self.cameras[camera.id] = [camera, CameraRecoder(camera)]
            self.cameras[camera.id][1].start()

        self.cameras_lock.release()

        print self.cameras



    #todo
    #add camera timeout
    def run(self):
        while True:
            for key,[camera, thr] in self.cameras.iteritems():
                if not thr.isAlive():
                    try:
                        self.cameras[camera.id][1] = CameraRecoder(camera)
                        self.cameras[camera.id][1].start()
                    except:
                        pass
                    
            time.sleep(50000)

    def remove_camera(self, camera):
        self.cameras_lock.acquire()
        if self.cameras.get(camera.id):
            self.cameras[camera.id][1].on = False
            del self.cameras[camera.id]
        self.cameras_lock.release()