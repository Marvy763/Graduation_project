# load libraries

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

import warnings
warnings.filterwarnings("ignore")
import os


# error : I tensorflow/core/platform/cpu_feature_guard.cc:142] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use 
# the following CPU instructions in performance-critical operations:  AVX2 FMA
# To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #solved error
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# load model
load_model = tf.keras.models.load_model(os.path.join('flask_src/static/uploaded_model/', 'project_model.h5'))
classes_dir = ["Adenocarcinoma","Large cell carcinoma","Normal","Squamous cell carcinoma"]




def chestScanPrediction(path):
    # Loading Image
    img = image.load_img(path, target_size=(224,224))
    # Normalizing Image
    norm_img = image.img_to_array(img)/255
    # Converting Image to Numpy Array
    input_arr_img = np.array([norm_img])
    # Getting Predictions
    pred = np.argmax(load_model.predict(input_arr_img))
    # Printing Model Prediction
    # print(classes_dir[pred])
    # return classes_dir[pred]
    return pred


def pred_info(argument):
    switcher = {
        0: {
        "Status" : "malignant",
        "Type": f"{classes_dir[argument]}",
        "Description": '''Lung adenocarcinoma is the most common form of lung cancer
accounting for 30 percent of all cases overall and about 40 percent
of all non-small cell lung cancer occurrences. Adenocarcinomas are
found in several common cancers, including breast, prostate and colorectal.
Adenocarcinomas of the lung are found in the outer region of the lung
in glands that secrete mucus and help us breathe.
Symptoms include coughing, hoarseness, weight loss and weakness.'''
        },
        1: {
        "Status": "malignant",
        "Type" : f"{classes_dir[argument]}",
        "Description" : '''Large-cell undifferentiated carcinoma: Large-cell undifferentiated carcinoma lung cancer grows and spreads quickly and can
be found anywhere in the lung. This type of lung cancer usually accounts for 10
to 15 percent of all cases of NSCLC.
Large-cell undifferentiated carcinoma tends to grow and spread quickly.'''
        },
        2: {
        "Status": "Normal",
        "Type": f"{classes_dir[argument]}",
        "Desription":"No Description is available"
        },
        3: {
        "Status":"malignant",
        "Type": f"{classes_dir[argument]}",
        "Description": '''Squamous cell: This type of lung cancer is found centrally in the lung,
where the larger bronchi join the trachea to the lung,
or in one of the main airway branches.
Squamous cell lung cancer is responsible for about 30 percent of all non-small
cell lung cancers, and is generally linked to smoking.'''
        }
    }

    # be assigned as default value of passed argument
    return switcher.get(argument, "nothing")
   