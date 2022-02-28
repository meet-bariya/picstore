from distutils.log import debug
from flask import Flask, request, redirect
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = 'photos'

blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)

try:
     container_client = blob_service_client.get_container_client(container=container_name)
     container_client.get_container_properties()
except:
     container_client = blob_service_client.create_container(container_name)

@app.route("/")
def view_photos():

     blob_item = container_client.list_blobs()

     img_html = ""

     for blob in blob_item:
          blob_client = container_client.get_blob_client(blob=blob.name)
          img_html += "<img src='{}' width='150px' style='margin:20px 15px' height='150px' />".format(blob_client.url)

     return """
          <head>
          <!-- CSS only -->
               <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
          </head>
          <body>
               <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                    <div class="container">
                         <a class="navbar-brand" href="/"> Picstore </a>
                    </div>
               </nav>
               <div class="container">
                    <div class="card" style="margin: 1em 0; padding: 1em 0 0 0; align-items: center;">
                         <h3>Upload new File</h3>
                         <div class="form-group">
                              <form method="post" action="/upload-photos" 
                              enctype="multipart/form-data">
                              <div style="display: flex;">
                                   <input type="file" accept=".png, .jpeg, .jpg, .gif" name="photos" multiple class="form-control" style="margin-right: 1em;">
                                   <input type="submit" value="upload" class="btn btn-primary">
                              </div>
                              </form>
                         </div> 
                    </div>
          """ + img_html + "</div></body>"

@app.route("/upload-photos", methods=["POST"])
def upload_photos():
     filenames=""
     for file in request.files.getlist("photos"):
          try:
               container_client.upload_blob(file.filename, file)
               filenames += file.filename + " "
          except Exception as e:
               print(e)

     return redirect ("/")

if __name__ == "__main__":
     app.run()