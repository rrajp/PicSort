import os
from tkinter import Tk

import cv2
import easygui
import face_recognition

root = Tk()
root.resizable(True, True)
root.geometry('100x100')

image = cv2.imread("img/RR.jpeg")
print(image.shape, image.size)
resize_factor = 0.25 if image.size > 31457280 else 1  # 30 mb
small_image = cv2.resize(image, (0, 0), fx = resize_factor, fy = resize_factor)
face_locations = face_recognition.face_locations(small_image)
count = 0
offset_factor = 0.1
print(len(face_locations))
for (top, right, bottom, left) in face_locations:
    top *= 1 / resize_factor
    right *= 1 / resize_factor
    bottom *= 1 / resize_factor
    left *= 1 / resize_factor
    v_offset = int((bottom - top) * offset_factor)
    h_offset = int((right - left) * offset_factor)
    print(v_offset, type(v_offset))
    print(h_offset, type(h_offset))
    try:
        crop_img = image[int(top) - v_offset:int(bottom) + v_offset, int(left) - h_offset:int(right) + h_offset]
        cv2.imwrite("tmp.jpg", crop_img)
        person_name = easygui.enterbox("Who is this person? ", image = "tmp.jpg", root = root)
        os.rename("tmp.jpg", "%s.jpg" % person_name)
    except Exception as e:
        offset = 0
        print(e)
        crop_img = image[top - offset:bottom + offset, left - offset:right + offset]
        cv2.imwrite("tmp.jpg", crop_img)
        person_name = easygui.enterbox("Who is this person? ", image = "tmp.jpg", root = root)
        os.rename("tmp.jpg", "%s.jpg" % person_name)
    count += 1
    exit(0)
