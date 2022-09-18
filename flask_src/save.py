import os
from werkzeug.utils import secure_filename
import uuid as uuid
import pickle

model = pickle.load(open('flask_src/static/model/finalized_model.sav', 'rb'))
def save_image(img):
    # grab image file name
    pic_filename = secure_filename(img.filename)

    # make image unique
    pic_name = str(uuid.uuid1()) + '_' + pic_filename

    img.save(os.path.join('flask_src/static/uploaded_img/', pic_name))
    dst =os.path.join('flask_src/static/uploaded_img/', pic_name)

    return pic_name,dst