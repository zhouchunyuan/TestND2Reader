# tested with python3.5 on win7 64bit
from nd2reader import ND2Reader

import matplotlib
import matplotlib.pyplot as plt
from PIL import Image # pip3 install Pillow to get PIL in python3.5

with ND2Reader('test.nd2') as images:
    print(images.metadata)# this is a simple metadata
    
    plt.imshow(images[2])# the image now is same as a numpy array
    
    plt.show()

    im = Image.fromarray(images[0])
    im.save('test.tif')# show how to save as tif with original data
    
    matplotlib.image.imsave('name.png', images[0])# here save as PNG


    appinfo = images.parser._raw_metadata.app_info
    # the raw metadata is retrieved by parser._raw_metadata
    # the contents is orderedDict, created from xml structure
    # So I have to use cascade [] to access an item
    ver = appinfo['variant']['no_name']['m_VersionString']['@value']
    print(ver)# this is to detect NIS-Elements version

    li = images.parser._raw_metadata.image_metadata_sequence
    metadata = li[b'SLxPictureMetadata']# this is a one-item dict
    # Howevr, the value in this item is a list which is very long
    # here we can obtain the objective name and also almost all important infomation.
    print(metadata[b'wsObjectiveName']) # this is how to get objective information   


