import os

from werkzeug.utils import secure_filename

import app


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.ALLOWED_EXTENSIONS


def file_save(file, id):
    if file.filename == '':
        raise Exception('error no selected file')

    # save files with secure name to avoid unnecessary access leak
    if file and allowed_file(file.filename):
        file.filename = (id + file.filename)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.UPLOAD_FOLDER, filename))
        return filename
    else:
        raise Exception('File format not supported - Upload a CSV file')
