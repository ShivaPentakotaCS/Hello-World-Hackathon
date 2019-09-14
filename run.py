from flask import Flask, render_template, send_file, escape, request
import subprocess, PyPDF2, os, time

app = Flask(__name__)

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
    uploadedFolder = request.files['folder']
    print("THIS IS TYPE:   " + str(type(uploadedFolder)))
    print("THIS IS FOLDER:   " + str(uploadedFolder))
    uploadedFolderName = "Uploaded_Folder"
    # change uploaded folder name to "Uploaded_Folder"
    
    for folderName, subfolders, filenames in os.walk(os.path.join('.', uploadedFolderName)):
        for filename in filenames:
            if filename.endswith('.pdf'):
                originalPdf = open(os.path.join(folderName, filename), 'rb')
                pdfReader = PyPDF2.PdfFileReader(originalPdf)
                if not pdfReader.isEncrypted:
                    pdfWriter = PyPDF2.PdfFileWriter()
                    for pageNum in range(pdfReader.numPages):
                        pdfWriter.addPage(pdfReader.getPage(pageNum))
                    if password2 != "":
                        pdfWriter.encrypt(password2)
                        resultPdf = open(os.path.join(uploadedFolderName, filename + '_Encrypted.pdf'), 'wb')
                        pdfWriter.write(resultPdf)
                        originalPdf.close()
                        resultPdf.close()
                        subprocess.Popen(["zip", "-y", "-e", "-P", password1, os.path.join(uploadedFolderName, filename + '.zip'), os.path.join(uploadedFolderName, filename + '_Encrypted.pdf')])
                    else:
                        pdfWriter.encrypt(password1)
                        resultPdf = open(os.path.join(uploadedFolderName, filename + '_Encrypted.pdf'), 'wb')
                        pdfWriter.write(resultPdf)
                        originalPdf.close()
                        resultPdf.close()
                        os.remove(os.path.join(uploadedFolderName, filename))

    time.sleep(1) # without waiting like this, there is risk that one of .pdf.zip will be deleted.
    for folderName, subfolders, filenames in os.walk(os.path.join('.', uploadedFolderName)):
        for filename in filenames:
            if password2 != "" and not filename.endswith('.pdf.zip'):
                os.unlink(os.path.join(uploadedFolderName, filename))
            elif password2 == "" and not filename.endswith('_Encrypted.pdf'):
                os.unlink(os.path.join(uploadedFolderName, filename))

    subprocess.check_output(["rm", "-rf", uploadedFolderName + ".zip"])
    subprocess.check_output(["zip", "-r", uploadedFolderName + ".zip", uploadedFolderName])
    subprocess.check_output(["rm", "-rf", uploadedFolderName])

    return render_template('results.html', zippedFolderName=uploadedFolderName + ".zip")

@app.route('/<zippedFolderName>.zip')
def copiedWebsite(zippedFolderName):
    return send_file(escape(zippedFolderName) + '.zip')

if __name__ == '__main__':
    app.run(debug=True)
