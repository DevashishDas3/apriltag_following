import cv2
from pid import PID
from bluerov_interface import BlueROV
import numpy as np
import tag_detection as td
from dt_apriltags import Detector

dv = td.TD()

vid = dv.get_video()

frame = dv.get_frame()