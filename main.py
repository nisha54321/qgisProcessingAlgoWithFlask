import sys
path1 = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms','/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/QNEAT3']
for i in path1:
    sys.path.append(i)

import qgis
from qgis.core import *    
from qgis.core import (
     QgsApplication, 
     QgsProcessingFeedback, 
     QgsVectorLayer
)
import processing
from qgis import processing

from qgis.analysis import QgsNativeAlgorithms
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()


from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())


from logging import debug
from flask import Flask, request, render_template, jsonify
import psycopg2
from werkzeug.utils import secure_filename
import os

from pca import pcaalgo

app = Flask(__name__)
app.secret_key = "my12346secretiskey" 

path1 = os.getcwd()
UPLOAD_FOLDER = os.path.join(path1, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['gpkg','shp','tif','gpkg','sdat','jp2'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", database="project")
cursor = connection.cursor()

@app.route("/", methods= ['GET', 'POST'])
def index():

    #add dropdown algo name
    cursor.execute("SELECT name FROM algorithm ")
    name = cursor.fetchall()

    name = [str(i).replace("('","").replace("',)","")for i in name]
        
    return render_template("demo2.html",algonames=name)

parameter = []
algoname = []
@app.route("/get_data", methods= ['GET', 'POST'])
def get_data():

    ##add parameter as label
    if request.method == 'POST':
        json_data = request.get_json()
        a_name = json_data['dd']
        algoname.append(a_name)

        squery1 = "SELECT description FROM algorithm where name = "+"'"+a_name+"'"
        para1 = cursor.execute(squery1)
        des = cursor.fetchall()
        print(des[0])

        squery = "SELECT parameter FROM algorithm where name = "+"'"+a_name+"'"
        para = cursor.execute(squery)
        paraval = cursor.fetchall()

        pname= paraval[0]

        for i in pname:
            label1 = list(i.split(","))
        print("parameter :",label1)

        for i in label1:
            parameter.append(i)

    #return render_template("demo2.html",description=des)

    return jsonify(label1)

value = []
minput = []
bands = []
@app.route("/run", methods= ['GET', 'POST'])
def run():
    aname = algoname[0]

    print(aname)
    grd = []
    ##take value of parameters (textbox , brows input)
    if request.method == 'POST':
        for val in parameter:
            if val == "INPUT" :
                files = request.files.getlist('INPUT[]')

                if aname =="gdal:merge" or aname == "gdal:merge(Image Mosaic)":
                    print("merge :", files)
                    aname ="gdal:merge"
                    for file in files:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        ip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        minput.append(ip)

                    value.append(minput)

                else:   
                    print("input")               
                    filename = secure_filename(files[0].filename)
                    files[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    ip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    value.append(ip)
            
            elif val == "GRIDS":
                print("grid ")     
                files = request.files.getlist('GRIDS[]')
          
                filename = secure_filename(files[0].filename)
                files[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                grd.append(ip)
                value.append(grd)

            elif val == "LAYERS":
                layers = []
                print("layers : ")     
                make = request.form['LAYERS']
                layers.append(make)
                value.append(layers)

            elif val == "SPECTRAL":
                print("input")     
                files = request.files.getlist('SPECTRAL[]')
          
                filename = secure_filename(files[0].filename)
                files[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                value.append(ip)

            elif val == "PANCHROMATIC":
                print("input") 
                files = request.files.getlist('PANCHROMATIC[]')
              
                filename = secure_filename(files[0].filename)
                files[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                value.append(ip)

            elif val == "RESAMPLING" :
                cmethod =["Binary Encoding","Parallelepiped","Minimum Distance","Mahalanobis Distance","Maximum Likelihood"]

                resample = ["Bilinear","Cubic","Nearest Neighbour","Cubic Spline","Average","Lanczos Windowed Sinc"]
                make = request.form['RESAMPLING']
                rval = resample.index(make)
                value.append(rval)

            elif val == "METHOD" :
                cmethod =["Binary Encoding","Parallelepiped","Minimum Distance","Mahalanobis Distance","Maximum Likelihood"]

                resample = ["Bilinear","Cubic","Nearest Neighbour","Cubic Spline","Average","Lanczos Windowed Sinc"]
                make = request.form['METHOD']
                rval = cmethod.index(make)
                value.append(rval)
            
            elif val == "BANDS" :
                make = request.form['BANDS']
                band = make.split(",")

                value.append(band)

            else:
                val1 = request.form[str(val)]
                value.append(val1) 

        algParaVal = {parameter[i]: value[i] for i in range(len(parameter))}
        
        print(algParaVal)

        if aname == "unsupervised (PCA)":
            print("pca running ......")
            pcaalgo(value[0], value[2], int(value[1]))

        else:
            #run algorithm
            print("qgis algorithm running............")
            processing.run(aname,algParaVal)
        
    return jsonify("success to run Algorithm:")
    
@app.route("/output", methods= ['GET', 'POST'])
def output():

    return render_template("map.html")

if __name__ == '__main__':
    app.run(debug=True,port = '5441')
