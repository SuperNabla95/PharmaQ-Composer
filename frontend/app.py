"""
Created on Wed Oct 30 08:12:30 2019
@author: dgadler
File used to start up the Flask frontend
"""


#Dependencies on GoogleMaps-flask and Flask
from flask import Flask, render_template, request
from flask_googlemaps import GoogleMaps, Map
import socket
import cv2
from datetime import datetime
import requests
import shutil

PORT_DB_SERVICE = 5001

#Input: pharmacy_name(str): the name of the pharmacy to be displayed on the infobox
#       cur_number_people(int): the number of people currently in line.
#       pharmacy_id(int): the id of the pharmacy
#       last_updated_time(str), the last updated time of this pharmacy
#Output: string, the content of the infobox
def format_infobox(pharmacy_name, cur_number_people, pharmacy_id, last_updated_time):
    
    last_updated_time_formatted =  datetime.utcfromtimestamp(int(last_updated_time)).strftime('%Y-%m-%d %H:%M:%S')

    
    str_infobox_out = (  "<div class='marker-pharmacy'>"
                       + '<b> ' + pharmacy_name + '</b>' +  '<br>'
                       + '<b> Reported number of people in queue: </b> ' + str(cur_number_people) + '<br> <br>'
                       + "Last updated at: " + str(last_updated_time_formatted) + "<br>" 
                       + "Upload new file with people in queue: "
                       + "<form method='post' action='img_upload?pharmacy_id=" + str(pharmacy_id) +"'  enctype='multipart/form-data'>"
                       + "<input type='file' name='file' > <br>"
                       + "<input type='submit' value='Upload File'> <br>"
                       + "</form>"
                       + "</div>")
    
    print(str_infobox_out)

    return(str_infobox_out)

def read_markers_from_db():
    #For now, let's just create some dummy markers
    #let's perform a request to the microservice to get all the farmacie's data
    url = 'http://127.0.0.1:{port_dataservice}/farmacie'.format(port_dataservice=str(PORT_DB_SERVICE))
    request_farmacie = requests.get(url)
    
    list_farmacie = request_farmacie.json()
    
    #This list will be populated with all the markers loaded up from the external DB    
    markers_list = []
    
    #let's now iterate through every single 'farmacia' in the list of farmacies
    for json_farmacia in list_farmacie:
        
        marker_farmacia = {}
        marker_farmacia["icon"] = "static/assets/{}-dot.png".format(json_farmacia['color'])
        marker_farmacia["lat"] = json_farmacia["lat"]
        marker_farmacia["lng"] = json_farmacia["lng"]
        marker_farmacia["infobox"] = format_infobox(json_farmacia["name"], 
                                                    json_farmacia["people"], 
                                                    json_farmacia["id"],
                                                    json_farmacia["time"])
        
        markers_list.append(marker_farmacia)
            
    return(markers_list)




    
app = Flask(__name__, template_folder="templates", static_folder="static")

GoogleMaps(
    app,
    #DEMO key
    key="AIzaSyDjIq1gVxqzc5Si4LupueYBANG3m1vvlEI"
 
)



#Input: -image_path(str): a string containing the path to the image whose crowd is to be analyzed
#Output
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
    

@app.route('/img_upload' , methods=["POST"])
def img_upload():
    if request.method == 'POST':  
        #print(request.files)
        f = request.files['file']  
        
        #strimg
        file_name = f.filename
        f.save(file_name)  
        
        #Let's move the picture to a different folder as well in python
        shutil.move(f.filename, "./static/imgs_uploaded/" + str(file_name))
        
        response_json = perform_prediction("./static/imgs_uploaded/" + str(file_name))
        number_people = extract_number_people_response(response_json)
        
        #Let's now draw the bounding box around the image
        draw_bounding_box("./static/imgs_uploaded/" + str(file_name), "./static/imgs_processed/" + str(file_name), response_json)

        #PUT REQUEST to update the DB
        pharmacy_id = request.args.get('pharmacy_id')
        
        ts = int(datetime.utcnow().timestamp())
        #time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
        requests.put("http://127.0.0.1:"+ str(PORT_DB_SERVICE) + "/farmacie", json=dict(
            id = pharmacy_id,
            people = number_people,
            time = ts
        ))
        
        #Now we can load up the image and process it with ML algorithms
        return render_template('img_upload.html', file_name=file_name, number_people=number_people,
                               pharmacy_id=pharmacy_id)



@app.route('/' , methods=["GET"])
def fullmap():
    #Reload all the data every time
    markers_farmacie = read_markers_from_db()
    
    fullmap = Map(
        identifier="fullmap",
        varname="fullmap",
        style=(
            "height:90%;"
            "width:100%;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=46.4892313, 
        lng=11.3121382,
        markers=markers_farmacie,
        zoom="14.2"
    )
          
    #Let's pass parameters over to the template over here!
    return render_template(
        'index.html',
        fullmap=fullmap,
        GOOGLEMAPS_KEY=request.args.get('apikey')
    )
    

my_ip = socket.gethostbyname(socket.gethostname())

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host=my_ip, port='5000')
