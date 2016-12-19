import caffe
import numpy as np
import matplotlib.pyplot as plt
#from misc.utils import *
from functions import *
from caffe_VGG_19 import *
from skimage.io import imsave

N = 50 # number of iterations of the GD
I = 3 # index of the layer
alpha = 1
beta = 1

photo_path = "../Images/dieux_du_stade.jpg"
art_path = "../Images/nuit_etoilee.jpg"

caffe.set_device(0)
caffe.set_mode_gpu()

model_path = "model/VGG_ILSVRC_19_layers_deploy.prototxt"
train_path = "model/VGG_ILSVRC_19_layers.caffemodel"
mean_path = "models/ilsvrc_2012_mean.npy"

net = caffe.Net(model_path, train_path, caffe.TEST)
VGG_MEAN = np.load(mean_path)

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2, 0, 1))
transformer.set_mean('data', VGG_MEAN)
transformer.set_raw scale('data', 255)
transformer.set_channel_swap('data', (2, 1, 0))

photo = caffe.io.load_image(photo_path)
art = caffe.io.load_image(art_path)
plt.imshow(photo)
plt.imshow(art)

transformed_inputs = transformer.preprocess('data', [photo, art])
net.blobs['data'].data[...] = transformed_inputs

net.forward()

feat_maps = ["conv1_1", "conv2_1", "conv3_1", "conv4_1", "conv5_1"]

p_features = []
a_features = []

for layer in feat_maps:
    p_features.append(net.blobs[layer].data[0, :])
    a_features.append(net.blobs[layer].data[1, :])

output = photo
output_transformed = transformer.preprocess('data', output)

for step in np.arange(N):
    net.blobs['data'].data[...] = output_transformed
    net.forward()

    o_features = []
    for layer in feat_maps:
        o_features.append(net.blobs[layer].data[0, :])

    loss, grad = compute_transfer_loss(o_features, p_features, a_features, \
                    I, alpha, beta) # TODO : code the loss function

    output_transformed = minimize(loss, output_transformed, grad)

output = transformer.deprocess('data', output_transformed)

imsave("../Images/out/output.jpg", output)
