import swiftclient
import keystoneclient
import os
from pydes import *
from flask import Flask, render_template, request, redirect
from flask import flash, request, session, abort, url_for
import mysql.connector


app = Flask(__name__)
k = pyDes.des(b"DESCRYPT", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

#IBM bluuemix app Environmwnt variables of the app.
auth_url = "https://identity.open.softlayer.com/v3"
password = "M1YYP6Ij0v_u4b^n"
project_id = "9defc13bceb0491c9d75f53fcbcee9cc"
user_id = "1dc102bb5d094f5f98a50e2c6ee73b47"
region_name = "dallas"

conn = swiftclient.Connection(key=password,
                              authurl = auth_url,
                              auth_version = '3',
os_options = {"project_id" : project_id,
              "user_id": user_id,
              "region_name": region_name})

cnx = mysql.connector.connect(user='becd56390a03dc', password='869071d3',
                              host='us-cdbr-iron-east-04.cleardb.net',
                              database='ad_20519ea5021ca79')
print "Connection Done"

container_name = 'sagar_test_container'
conn.put_container(container_name)
print "Container %s created successfully." %container_name

  
@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def do_admin_login():
    cursor = cnx.cursor()
    if request.method == 'GET':
        return render_template('login.html')
    User_Name = request.form['username']
    Passowrd = request.form['password']
    query = "SELECT * FROM USERS WHERE User_Name=\'"+User_Name+"\'"+" AND "+"USER_PASSWORD = \'"+Passowrd+"\'"
    cursor.execute(query)
    for (User_ID, User_Name, User_Password) in cursor:
        print User_Name
        return render_template('index.html')
    cursor.close()
    cnx.close()
    flash('Logged in successfully')
    return redirect(url_for('index'))

@app.route("/upload", methods=['GET','POST'])
def upload():
        if request.method=='POST':
                file_name = request.files['file_upload'].filename
                content=request.files['file_upload'].read()
                encryptedD = k.encrypt(content)
                size_of_file= os.path.getsize(file_name)
                if (size_of_file<=1000000) :
                        conn.put_object(container_name,
                        file_name,  
                        contents= encryptedD,
                        content_type='text')
                else:
                        print "File limit Reached!!"
                return '<h1>Awesome! File uploaded Successfully.<h1><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route("/download", methods=['GET','POST'])
def download():
        if request.method=='POST':
                filename = request.form['file_download']
                filedownload = conn.get_object(container_name,filename)
                with open(filename, 'w') as file_downloaded:
                        fileContentsBytes = filedownload[1]
                        fileContents = k.decrypt(fileContentsBytes).decode('UTF-8')
                        file_downloaded.write(fileContents)
                return '<h1>Awesome! File Downloaded Successfully.<h1><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/delete',methods=['GET','POST'])
def Delete():
    if request.method=='POST':
      filename = request.form['file_delete']
      file = conn.delete_object(container_name,filename)
      return '<h3>The File has been successfully deleted,</h3><br><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/list')
def List():
        listOfFiles = ""
        for container in conn.get_account()[1]:
                for data in conn.get_container(container['name'])[1]:
                        if not data:
                                listOfFiles = listOfFiles + "<i> No files are currently present on Cloud.</i>"
                        else:
                                listOfFiles = listOfFiles + "<li>" + 'File: {0}\t Size: {1}\t Date: {2}'.format(data['name'], data['bytes'], data['last_modified']) + "</li><br>"
        return '<h3>The files currently on cloud are </h3><br><br><ol>' + listOfFiles + '<br><form action="../"><input type="Submit" value="Lets go back"></form>'


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
