# tested with python3.5 on win7 64bit
from nd2reader import ND2Reader
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image # pip3 install Pillow to get PIL in python3.5

#############################################
# find a key value in dict tree
#############################################
def findkey(key,dic):
    ret = None
    if key in dic:
        ret = dic[key]
    else:
        for k,v in dic.items():
            if(type(v) == type(dic)):
                ret = findkey(key,v)
                if(ret is not None):
                    break
    return ret
                
            
#############################################
# a function to expand orderedDict
# using recursion algorithm
#############################################
def expand(dic,idx):
    idx+=1
    tab = '  '
    print(tab*idx)
    for k,v in dic.items():
        print(tab*idx,k,':',end='')
        if(type(v) != type(dic)):
            print(tab*idx,v)
        else:
            expand(v,idx)

###############################################      
# to get the (min,max) for channel ch using lut
###############################################
def getLUTLowHigh(rawMetaData,ch):
    
    bitDepth = findkey(b'uiBpc',rawMetaData.image_metadata_sequence)
    lut = rawMetaData.lut_data

    try:
        if('m_sLutParam' in lut['variant']['no_name']):
            lutParam = lut['variant']['no_name']['m_sLutParam']['sCompLutParam']
            # here we want to access the item by number index
            # So first convert OrderedDict to list
            keys = list(lutParam)
            #but the list only refer to keys
            #So we have to use it as keys
            lutMin = int(lutParam[keys[ch+1]]['uiMinSrc']['@value'])
            lutMax = int(lutParam[keys[ch+1]]['uiMaxSrc']['@value'])
        else:
            lutMin = 0
            lutMax = 2**bitDepth - 1
        return(lutMin,lutMax)
    except Exception as e:
        print('error:'+e)
        return None
            
filename = 'test.nd2'


with ND2Reader(filename) as images:
    #print(images.metadata)# this is a simple metadata

    rawMetaData = images.parser._raw_metadata # here is a full version of metadata
    lut         = rawMetaData.lut_data
    #print('-----\n',lut,'\n------') #lut is a complicated block of xml
    #expand(lut,0) # uncomment this to see the tree

    lutMinMax = getLUTLowHigh(rawMetaData,0)

    appinfo     = rawMetaData.app_info
    # the raw metadata is retrieved by parser._raw_metadata
    # the contents is orderedDict, created from xml structure
    # So I have to use cascade [] to access an item
    ver = appinfo['variant']['no_name']['m_VersionString']['@value']
    #print(ver)# this is to detect NIS-Elements version

    li = rawMetaData.image_metadata_sequence
    metadata = li[b'SLxPictureMetadata']# this is a one-item dict
    # Howevr, the value in this item is a list which is very long
    # here we can obtain the objective name and also almost all important infomation.
    obj = metadata[b'wsObjectiveName'] # this is how to get objective information   
    #expand(li,0)

    bitDepth = findkey(b'uiBpc',li)
    #expand(rawMetaData.grabber_settings,0)

    txtMsg = ''
    ##########################################
    # this part is to test
    # if the image is too dark
    # under current LUT
    #
    #imax = 2**bitDepth-1
    imax = lutMinMax[1]
    hist_ret = np.histogram(images[0],[0,int(imax/3),int(imax/3*2),imax])
    hist = hist_ret[0]#the first is the hist, and the 2nd is bin edges
    if ( hist[0]/np.sum(hist)>0.99):
        txtMsg = str(bitDepth)+'bit image! The current LUT is too dark\n'


    ####### below is to display and save it #############
    txtMsg += str(ver)+'\n'+str(obj) 
    plt.text(0, -10, txtMsg, fontsize=10)
    plt.imshow(images[0],cmap="gray",clim=lutMinMax)# the image now is same as a numpy array
    plt.show()

    im = Image.fromarray(images[0])
    im.save('test.tif')# show how to save as tif with original data

    matplotlib.image.imsave('name.png', arr=images[0],cmap="gray",vmin=lutMinMax[0],vmax=lutMinMax[1])# here save as PNG
