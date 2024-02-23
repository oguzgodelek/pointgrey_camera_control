import json
import cv2 as cv
import numpy as np
import camera_control as camera
from time import time

def nothing(x):
    pass

def panel():
    cam = camera.PointgreyCamera()
    out = cv.VideoWriter('arena_record_new_{}.mp4'.format(time()), cv.VideoWriter_fourcc('m', 'p', '4', 'v'), 15, (4000, 3000), False)
    parameters = None
    with open('parameters.json', 'r') as file:
        parameters = json.load(file)

    cv.namedWindow('Control Panel')
    cv.createTrackbar('Exposure Time', 'Control Panel', 1, 45, nothing)
    cv.createTrackbar('Gain', 'Control Panel', 0, 24, nothing)

    cv.setTrackbarMin('Gain', 'Control Panel', int(cam.min_gain))
    cv.setTrackbarMax('Gain', 'Control Panel', int(cam.max_gain))

    cv.setTrackbarMin('Exposure Time', 'Control Panel',
                      int(cam.min_exposure_time / 1000))
    cv.setTrackbarMax('Exposure Time', 'Control Panel',
                      int(cam.max_exposure_time / 1000))

    cv.setTrackbarPos("Exposure Time", "Control Panel", parameters['exposure'])
    cam.set_exposure_time(parameters['exposure'])

    cv.setTrackbarPos("Gain", "Control Panel", parameters['gain'])
    cam.set_gain(parameters['gain'])


    print(cam.min_exposure_time, cam.max_exposure_time)
    while True:
        last_exposure = parameters['exposure']
        last_gain = parameters['gain']

        parameters['exposure'] = cv.getTrackbarPos('Exposure Time',
                                                   'Control Panel')
        parameters['gain'] = cv.getTrackbarPos('Gain',
                                               'Control Panel')

        if last_exposure != parameters['exposure']:
            cam.set_exposure_time(parameters['exposure'])
        if last_gain != parameters['gain']:
            cam.set_gain(parameters['gain'])


        ret, frame = cam.read()
        out.write(frame)
        frame = cv.resize(frame, (1000, 750), -1, cv.INTER_LINEAR)
        cv.imshow('Control Panel', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    del cam
    cv.destroyAllWindows()
    out.release()
    with open('parameters.json', 'w') as file:
        json.dump(parameters, file)

def test():
    cam = camera.PointgreyCamera()
    cam.read()


if __name__ == '__main__':
    panel()
