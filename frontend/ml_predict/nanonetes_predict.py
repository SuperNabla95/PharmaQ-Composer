#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 16:57:11 2020

@author: daniele
"""

import requests
import cv2
from sightengine.client import SightengineClient

#Input: -image_path(str): a string containing the path to the image whose crowd is to be analyzed
def perform_prediction(image_path):
    url = 'https://app.nanonets.com/api/v2/ObjectDetection/Model/5305efe3-f03e-4e79-b4d9-b6bebb78ebc9/LabelFile/'
    
    data = {'file': open(image_path, 'rb')}
    response = requests.post(url, auth=requests.auth.HTTPBasicAuth('5kZQ1enyezAt0BeHuYkGlx1XP5WYvyFY', ''), files=data)
    return(response.json())

def extract_number_people_response(response_json):
    number_people = len(response_json["result"][0]["prediction"])
    return(number_people)

def draw_bounding_box(source_image, destination_image, response_json):
    
    rectangles_list = response_json["result"][0]["prediction"]
    
    image = cv2.imread(source_image)

    for rectangle in rectangles_list:
        cv2.rectangle(image,(rectangle["xmin"],rectangle["ymin"]),(rectangle["xmax"],rectangle["ymax"]),(255,0,0),5) # add rectangle to image
        
    cv2.imwrite(destination_image,image)


#Detect people in the image
response_json = perform_prediction("./images_queue/intesa_san_paolo_queue.jpg")
number_people = extract_number_people_response(response_json)
print("There are " + str(number_people) + " people in this picture")
#
#response_json = perform_prediction("./trento_images/farmacia_queue.jpg")
#number_people = extract_number_people_response(response_json)
#print("There are " + str(number_people) + " people in this picture")


