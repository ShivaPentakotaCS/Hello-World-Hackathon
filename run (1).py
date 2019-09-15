from flask import Flask, render_template, send_file, escape, request
import subprocess, PyPDF2, os, time
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/harry/Desktop/Flask_Hackathon/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/results", methods = ['POST'])
def results():
    password1 = request.form['password 1'].encode("utf-8")
    password2 = request.form['password 2'].encode("utf-8")
    uploadedFolder = request.files.getlist('folder')

    for fileInstance in uploadedFolder:
        fileInstance.save(os.path.join(app.config['UPLOAD_FOLDER'], str(fileInstance.filename)[int(str(fileInstance.filename).find('/'))+1:]))

    uploadedFolderName = "Uploaded_Folder"
    subprocess.Popen(["mkdir", uploadedFolderName])

    for folderName, subfolders, filenames in os.walk(os.path.join('.')):
        for filename in filenames:
            if folderName != "./templates" and folderName != "./static" and filename != "run.py" and filename.endswith('.pdf'):
                originalPdf = open(os.path.join(folderName, filename), 'rb')
                pdfReader = PyPDF2.PdfFileReader(originalPdf)
                if not pdfReader.isEncrypted:
                    pdfWriter = PyPDF2.PdfFileWriter()
                    for pageNum in range(pdfReader.numPages):
                        pdfWriter.addPage(pdfReader.getPage(pageNum))
                    if password2 != "":
                        pdfWriter.encrypt(password2)
                        resultPdf = open(os.path.join(folderName, filename + '_Encrypted.pdf'), 'wb')
                        pdfWriter.write(resultPdf)
                        originalPdf.close()
                        resultPdf.close()
                        subprocess.Popen(["zip", "-y", "-e", "-P", password1, os.path.join(folderName, filename + '.zip'), filename + '_Encrypted.pdf'])
                        time.sleep(0.1)
                        subprocess.Popen(["mv", os.path.join(folderName, filename + '.zip'), os.path.join(uploadedFolderName, filename + '.zip')])
                    else:
                        pdfWriter.encrypt(password1)
                        resultPdf = open(os.path.join(folderName, filename + '_Encrypted.pdf'), 'wb')
                        pdfWriter.write(resultPdf)
                        originalPdf.close()
                        resultPdf.close()
                        subprocess.Popen(["mv", os.path.join(folderName, filename + '_Encrypted.pdf'), os.path.join(uploadedFolderName, filename + '_Encrypted.pdf')])

    time.sleep(1) # nececssary
    for folderName, subfolders, filenames in os.walk('.'):
        for filename in filenames:
            if folderName != "./" + uploadedFolderName and folderName != "./templates" and folderName != "./static" and filename != "run.py":
                os.unlink(os.path.join(folderName, filename))

    subprocess.check_output(["rm", "-rf", uploadedFolderName + '.zip'])
    subprocess.check_output(["zip", "-r", uploadedFolderName + ".zip", uploadedFolderName])
    subprocess.check_output(["rm", "-rf", uploadedFolderName])

    return render_template('results.html', zippedFolderName=uploadedFolderName)

@app.route('/<zippedFolderName>.zip')
def dwnloadZippedFolder(zippedFolderName):
    return send_file(escape(zippedFolderName) + '.zip')

if __name__ == '__main__':
    app.run(debug=True)
