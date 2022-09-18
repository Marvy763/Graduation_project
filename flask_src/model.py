# -*- coding: utf-8 -*-
"""
Created on Sat May 14 05:34:27 2022

@author: asd
"""


# -*- coding: utf-8 -*-
"""
Created on Mon May  9 21:31:44 2022

@author: asd
"""



import glob
import cv2
import numpy as np
import matplotlib.pyplot  as plt 
from scipy.signal import convolve2d
import scipy.misc
import scipy.ndimage
from sklearn.neighbors import KNeighborsClassifier  
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler  
from sklearn.metrics import precision_score, confusion_matrix,recall_score, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import pandas as pd
import os
from skimage.transform import resize
from skimage.io import imread
import numpy as np
from scipy.signal import convolve2d
import scipy.misc
import scipy.ndimage
from scipy import stats
from skimage import img_as_ubyte
from skimage.filters import gaussian
import matplotlib.pyplot as plt
import pickle


datadir = 'C:/Users/marve/Pictures/BlueStacks/model/archive/Data/train' #root directory


categories = ['adenocarcinoma_left.lower.lobe_T2_N0_M0_Ib','large.cell.carcinoma_left.hilum_T2_N2_M0_IIIa',
             'normal','squamous.cell.carcinoma_left.hilum_T1_N2_M0_IIIa']

def preprocess(img):
    img_resized=resize(img,(150,150,3)) 
    gray = cv2.cvtColor(np.float32(img_resized), cv2.COLOR_RGB2GRAY)
    return gray

# flat_data_arr=[]
# target_arr=[]
# for i in categories:
    
#    print(f'loading... category : {i}')   
#    path=os.path.join(datadir,i) 
#    for img in os.listdir(path):  
#       img_array=imread(os.path.join(path,img))
#       flatData=preprocess(img_array)
#       flat_data_arr.append(flatData.flatten())   
#       target_arr.append(categories.index(i))   
#       print(f'loaded category:{i} successfully')
#       target=np.array(target_arr)

def normal(img1):
    img1 = img1 / img1.max() #normalizes data in range 0 - 255
    img1 = 255 * img1
    img1 = img1.astype(np.uint8)
    return img1
    
   
    
def extract_sift_features(image):

    image_descriptors = []
    sift = cv2.SIFT_create()
    #for image in list_image:
        
    kp,des=sift.detectAndCompute(image,None)
    x=cv2.drawKeypoints(image, kp, image.copy()) 
    image_descriptors.append(x)

    return image_descriptors    
    
# images=[]
# for data in flat_data_arr:
#     edge_image=normal(data)
#     flat_data=extract_sift_features(edge_image)
#     for i in flat_data:
        
#         images.append(i.flatten())
#     #images.append(edge_image)

##sift_res=[]
#for j in images:
    #flat_data=extract_sift_features(j)
    #sift_res.append(flat_data.flatten())


#flatted=[]
#for i in sift_res:
     #flatted.append(i)   
      
# xtrain,xtest,ytrain,ytest=train_test_split(images,target, test_size=0.25, random_state=42,stratify=target)
# model = SVC(C=1,kernel='poly',gamma='auto') 
# model.fit(xtrain, ytrain)  
# y_pred = model.predict(xtest)
# #from sklearn.metrics import precision_score, confusion_matrix,recall_score, f1_score
# #Plot the confusion matrix and get the confusion matrix matrics

# # save the model to disk
# filename = 'finalized_model.sav'
# pickle.dump(model, open(filename, 'wb'))
 
# # some time later...
 
# # load the model from disk
# loaded_model = pickle.load(open(filename, 'rb'))
# result = loaded_model.score(xtest, ytest)
# print(result)

# print('Accuracy: {:.2f}'.format(accuracy_score(ytest, y_pred)))
# precision = precision_score(ytest, y_pred, average='micro')
# recall = recall_score(ytest, y_pred , average='micro')
# score = f1_score(ytest, y_pred , average='micro') 

# print('Precision: ',precision)
# print('Recall: ',recall)
# print('f1_score',score)

# image_path='5.png'      
def evaluation_model(image_path):
    c=imread(image_path)
    x=preprocess(c)
    zz=np.array(x)
    d=zz.flatten()
    y=normal(d)
    
    a=extract_sift_features(y)
    z=[]
    for j in a:
        z.append(j.flatten())
        
        
   
    # y_p = model.predict(z)
    
    return z
# b=evaluation_model(image_path)
# print(b)
classes_dir = ["Adenocarcinoma","Large cell carcinoma","Normal","Squamous cell carcinoma"]


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
   
   
    