import json
import os
from tkinter import *

import cv2
import face_recognition
import numpy as np

from helper_function.gui import gui

known_db = dict()
offset_factor = 0.1

if not os.path.exists("./known_img"):
    os.mkdir("./known_img")
if not os.path.exists("./db"):
    os.mkdir("./db")
if not os.path.exists("./img"):
    os.mkdir("./img")

if os.path.exists("./db/data.json"):
    fp = open('/home/ravirajprajapat/Documents/Learning/facerecognition/db/data.json').read()
    try:
        data_db = json.loads(fp)
    except:
        data_db = dict()
else:
    data_db = dict()


def search_name(klist, name):
    r = re.compile("%s.*" % name.lower())
    newlist = list(filter(r.match, klist))  # Read Note
    return len(newlist)


def save_image_with_offset(sdir, ddir, top, bottom, left, right, offset_factor, file_path):
    v_offset = int((bottom - top) * offset_factor)
    h_offset = int((right - left) * offset_factor)
    crop_img = image[int(top) - v_offset:int(bottom) + v_offset,
               int(left) - h_offset:int(right) + h_offset]
    cv2.imwrite(sdir + "tmp.jpg", crop_img)
    # person_name = gui("What is the name of this person? ", sdir + "tmp.jpg")
    person_name = gui("What is the name of this person? ", sdir + "tmp.jpg", False)
    if person_name.lower() == 'x':
        os.remove(sdir + "tmp.jpg")
        return
    data_db[file_path].append(person_name)
    number = search_name(list(known_db.keys()), person_name)
    print(person_name, number)
    filename = "{}-{}.jpg".format(person_name.lower(), str(number + 1))
    os.rename(sdir + "tmp.jpg", ddir + filename)
    known_db[filename.split('.')[0]] = \
        face_recognition.face_encodings(face_recognition.load_image_file(ddir + filename))[0]


def save_image(sdir, ddir, top, bottom, left, right, offset_factor, file_path):
    try:
        save_image_with_offset(sdir, ddir, top, bottom, left, right, offset_factor, file_path)
    except Exception:
        save_image_with_offset(sdir, ddir, top, bottom, left, right, 1, file_path)


if len(os.listdir('known_img')) > 0:
    for file in os.listdir('known_img'):
        if file != 'tmp.jpg':
            known_db[file.split('.')[0]] = \
                face_recognition.face_encodings(face_recognition.load_image_file(os.path.join('known_img', file)))[0]

for root, dirnames, filenames in os.walk('img'):
    for file in filenames:
        file_path = os.path.join(root, file)
        data_db[file_path] = list()

        image = cv2.imread(os.path.join(root, file))
        print(image.shape, image.size)
        resize_factor = 0.25 if image.size > 31457280 else 1  # 30 mb
        small_image = cv2.resize(image, (0, 0), fx = resize_factor, fy = resize_factor)
        face_locations = face_recognition.face_locations(small_image)
        face_encodings = face_recognition.face_encodings(small_image)
        count = 0

        print(len(face_locations))
        for i, (top, right, bottom, left) in enumerate(face_locations):
            matches = face_recognition.compare_faces(list(known_db.values()), face_encodings[i])
            name = "Unknown"
            face_distances = face_recognition.face_distance(list(known_db.values()), face_encodings[i])
            if len(matches) > 0:
                best_match_index = np.argmin(face_distances)
            else:
                best_match_index = 0
                matches.append(False)

            top *= 1 / resize_factor
            right *= 1 / resize_factor
            bottom *= 1 / resize_factor
            left *= 1 / resize_factor
            v_offset = int((bottom - top) * offset_factor)
            h_offset = int((right - left) * offset_factor)

            if matches[best_match_index]:
                name = list(known_db.keys())[best_match_index].split('-')[0]
                crop_img = image[int(top) - v_offset:int(bottom) + v_offset, int(left) - h_offset:int(right) + h_offset]
                cv2.imwrite("tmp.jpg", crop_img)
                # response = gui("Is this person %s" % name.capitalize(), "tmp.jpg")
                response = gui("Is this person %s" % name.capitalize(), "./tmp.jpg", True)
                if int(response) == 0:
                    save_image("", "known_img/", top, bottom, left, right, offset_factor, file_path)
                else:
                    data_db[file_path].append(name)
            else:
                save_image("known_img/", "known_img/", top, bottom, left, right, offset_factor, file_path)
        count += 1

with open('/home/ravirajprajapat/Documents/Learning/facerecognition/db/data.json', 'w') as fp:
    json.dump(data_db, fp)
    fp.close()
