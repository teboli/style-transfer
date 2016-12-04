#-*- coding:utf-8 -*-

import numpy as np
import tensorflow as tf
from custom_VGG import Vgg19
from tensor_functions import *
import utils
import skimage.io
from time import time

#loading images
photo = utils.load_image("./Images/argentine.jpg")
art   = utils.load_image("./Images/nuit_etoilee.jpg")

#resizing images
photo_batch = np.reshape(photo, (1, 224, 224, 3))
art_batch   = np.reshape(art, (1, 224, 224, 3))

#ratios structure vs style
alpha = 1
beta = 1

#layer where to exctract features_a
layer = 5

with tf.device('/cpu:0'):

    # session : get for the painting and the photo the features from convX.1
    with tf.Session() as sess:

        #creating a noisy output
        output = tf.Variable(255*tf.random_uniform([1,224,224,3]))

        init = tf.initialize_all_variables()
        sess.run(init)

        image = tf.placeholder(tf.float32, [1, 224, 224, 3])
        photo_dict = {image: photo_batch}
        art_dict   = {image: art_batch}
        out_dict   = {image: output.eval()}

        # creating the CNN
        cnn = Vgg19('./vgg19.npy')
        with tf.name_scope("photo"):
            cnn.build(image)

        # dictionnary of fetches
        fetches = (cnn.conv1_1, cnn.conv2_1, cnn.conv3_1, cnn.conv4_1, \
                       cnn.conv5_1)

        # running a session for photography featuresextraction
        photo_features = sess.run(fetches, feed_dict = photo_dict)
        #photo_features = np.zeros((1,224,224,3))
        print("Features extraction from photography, done !")

        # running a session for art piece features extraction
        art_features = sess.run(fetches, feed_dict = art_dict)
        #art_features = np.zeros((1,224,224,3))
        print("Features extraction from art piece, done !")

        # running a session for the output
        out_features = sess.run(fetches, feed_dict = out_dict)
        #out_features = 255*np.random.rand(1,224,224,3)
        print("Features extraction from noise, done !")

        # losses for each layer
        style_loss = style_error(art_features, out_features)
        #alpha_loss = alpha_reg(x=output, alpha=6, lambd=2.16e8)
        #beta_loss = TV_reg(x=output, beta=2, lambd=5)
        total_loss = np.zeros(5) + style_loss #+ alpha_loss + beta_loss
        for k in np.arange(5):
            total_loss[k] += structure_error(photo_features, out_features, k)
        print("Loss computation, done !")

        print(tf.trainaible_variables())

        # minimization of the loss
        l_rate = 0.5
        decay = 0.9
        opt = tf.train.GradientDescentOptimizer(learning_rate = l_rate)
        loss = total_loss[layer-1]
        train = opt.minimize(loss)
        print("Gradient descent construction, done !")

        # # let's begin !
        # sess.run(tf.initialize_all_variables())
        # for step in np.arange(5):
        #     sess.run(train)
        #     if (step%50 == 0):
        #         print("Optimization step : {}".format(step))
        #     output = sess.run(variables) # update of output
        #
        # # display the result
        # image_out = np.array(output)
        # skimage.io.imsave("./images/out/output.jpg", img)
