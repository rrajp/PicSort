import json
import os
from tkinter import *

import cv2
import face_recognition
import numpy as np

from helper_function.gui import gui

known_db = dict()

# Configurable Variables
offset_factor = 0.1
unknown_images_dir = './img/'
known_faces_dir = "./known_img/"
database_dir = "./db/"
database_file = "./db/data.json"
Training_Mode = FALSE

if Training_Mode:
    print("::: Important Note ::: \n Running the programme in Training Mode!!!")
else:
    print("::: Important Note ::: \n Running the programme in Auto Detection Mode!!!")

# checks existence of required folders and creates if not available
if not os.path.exists(known_faces_dir):
    os.mkdir(known_faces_dir)
if not os.path.exists(database_dir):
    os.mkdir(database_dir)
if not os.path.exists(unknown_images_dir):
    os.mkdir(unknown_images_dir)

# Checks db files and reads existing one.
if os.path.exists(database_file):
    fp = open(database_file).read()
    try:
        data_db = json.loads(fp)
    except:
        data_db = dict()
else:
    data_db = dict()


# Function to check if person name exists in known database
def search_name(klist, name):
    r = re.compile("%s.*" % name.lower())
    newlist = list(filter(r.match, klist))  # Read Note
    return len(newlist)


# Save the image of known in database with provided offset
def save_image_with_offset(sdir, ddir, top, bottom, left, right, offset_factor, file_path):
    v_offset = int((bottom - top) * offset_factor)
    h_offset = int((right - left) * offset_factor)
    crop_img = image[int(top) - v_offset:int(bottom) + v_offset,
               int(left) - h_offset:int(right) + h_offset]
    cv2.imwrite(sdir + "tmp.jpg", crop_img)
    # person_name = gui("What is the name of this person? ", sdir + "tmp.jpg")
    person_name = gui("What is the name of this person? ", sdir + "tmp.jpg", False)
    if person_name.lower() == 'x':
        data_db[file_path].append("Unknown")
        os.remove(sdir + "tmp.jpg")
        return
    data_db[file_path].append(person_name)
    print("{} : Adding {} to this Pic".format(file_path, person_name))
    number = search_name(list(known_db.keys()), person_name)
    filename = "{}-{}.jpg".format(person_name.lower(), str(number + 1))
    os.rename(sdir + "tmp.jpg", ddir + filename)
    print("{} : Saved {}'s image as {} in known faces".format(file_path, person_name, filename))
    known_db[filename.split('.')[0]] = \
        face_recognition.face_encodings(face_recognition.load_image_file(ddir + filename))[0]


# Save image with and without offset with try catch :
def save_image(sdir, ddir, top, bottom, left, right, offset_factor, file_path):
    try:
        save_image_with_offset(sdir, ddir, top, bottom, left, right, offset_factor, file_path)
    except Exception:
        save_image_with_offset(sdir, ddir, top, bottom, left, right, 1, file_path)


# Loading the known persons encoding on script start
if len(os.listdir(known_faces_dir)) > 0:
    for file in os.listdir(known_faces_dir):
        if file != 'tmp.jpg':
            print("Loading encodings of -", file)
            try:
                known_db[file.split('.')[0]] = \
                    face_recognition.face_encodings(
                        face_recognition.load_image_file(os.path.join(known_faces_dir, file)))[0]
            except:
                print("Couldn't Load encodings of - ", file)
                continue

# Main function starts here, walking through all the files in img directory
for root, dirnames, filenames in os.walk(unknown_images_dir):
    for file in filenames:
        file_path = os.path.join(root, file)
        print("Finding Faces in ", file_path)
        if file_path in data_db:
            print("Already processed {} earlier, hence skipiing for known, check data.json".format(file_path))
            continue
        if file.split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            print("Not processing {} file format".format(file))
            continue
        data_db[file_path] = list()

        image = cv2.imread(os.path.join(root, file))
        print(image.shape, image.size)
        if image.size > 10978112 and image.size < 31457280:
            resize_factor = 0.5
        elif image.size > 31457280:
            resize_factor = 0.25
        else:
            resize_factor = 1
        # resize_factor = 0.25 if image.size > 31457280 else 1  # 30 mb
        small_image = cv2.resize(image, (0, 0), fx = resize_factor, fy = resize_factor)
        face_locations = face_recognition.face_locations(small_image)
        face_encodings = face_recognition.face_encodings(small_image)
        count = 0

        print("Found total {} faces in : {}".format(len(face_locations), file))
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
                try:
                    crop_img = image[int(top) - v_offset:int(bottom) + v_offset,
                               int(left) - h_offset:int(right) + h_offset]
                    cv2.imwrite("tmp.jpg", crop_img)
                except:
                    crop_img = image[int(top):int(bottom),
                               int(left):int(right)]
                    cv2.imwrite("tmp.jpg", crop_img)
                # response = gui("Is this person %s" % name.capitalize(), "tmp.jpg")
                if Training_Mode:
                    response = gui("Is this person : %s" % name.capitalize(), "./tmp.jpg", True)
                    if int(response) == 0:
                        save_image("", known_faces_dir, top, bottom, left, right, offset_factor, file_path)
                    else:
                        data_db[file_path].append(name)
                else:
                    print("Found {} in : {}".format(name, file_path))
                    data_db[file_path].append(name)
            else:
                if Training_Mode:
                    save_image(known_faces_dir, known_faces_dir, top, bottom, left, right, offset_factor, file_path)
                else:
                    print("Found Unknown in : {}".format(file_path))
                    data_db[file_path].append("Unknown")
        count += 1

# Save found Photo-people data to directory
with open(database_file, 'w') as fp:
    json.dump(data_db, fp)
    fp.close()
