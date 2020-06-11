
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import numpy as np
import signal
from tensorflow.keras import layers
import time
from progress.bar import IncrementalBar
from progress.spinner import Spinner
from datasets import *
from utilsExp import *
tf.get_logger().setLevel('ERROR')
tf.get_logger().warning('test')

# Load the dataset from arrays
#trainDatasetArray = searchTrainDataset('e', 32500, 'experiment')
#trainDatasetArray = trainDataset('~vulnerable', 'experiment')

train_dataset = ''

# To prepare the dataset
BATCH_SIZE = 0 # Number of element from the dataset to be loaded in the model at the same time
SHUFFLE_BUFFER_SIZE = 500 # Number of element to make a shuffle in the dataset

#test_dataset = test_dataset.batch(BATCH_SIZE) For test the GAN

dataDimension = ''
generator = ''
discriminator = ''
# The generator model
def make_generator_model(dataDimension):
    model = tf.keras.Sequential()
    model.add(layers.Dense(dataDimension,
                           activation='relu',
                           kernel_initializer='he_uniform',
                           input_dim=dataDimension))
    model.add(layers.Dense(dataDimension, activation='sigmoid'))

    return model

# To test the generator from a noise array
# noise = tf.random.normal([1, 14])
# generated_image = generator(noise, training=False)
# print(generated_image)

# The discriminator model
def make_discriminator_model(dataDimension):
    model = tf.keras.Sequential()
    model.add(layers.Flatten(input_shape=(dataDimension,)))
    model.add(layers.Dense(dataDimension, activation='relu'))
    model.add(layers.Dense(1))

    return model


# To test the discriminator for a particular array
# decision = discriminator(generated_image)
# print("Decision: ->")
# print(decision)

# This method returns a helper function to compute cross entropy loss
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

# This method quantifies how well the discriminator is able to distinguish 
# real images from fakes. It compares the discriminator's predictions 
# on real images to an array of 1s, and the discriminator's predictions 
# on fake (generated) images to an array of 0s.
def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

# The generator's loss quantifies how well it was able to trick the discriminator.
# Intuitively, if the generator is performing well, the discriminator 
# will classify the fake images as real (or 1). Here, we will compare 
# the discriminators decisions on the generated images to an array of 1s.
def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)

# The discriminator and the generator optimizers are different 
# since we will train two networks separately.
# This is for the GAN model
generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

# Setting for the trainning process
EPOCHS = 0 # Number of iteration over the dataset
noise_dim = 0 # Noise dim, this is equal to the Generator output array 

# Notice the use of `tf.function`
# This annotation causes the function to be "compiled".
@tf.function
def train_step(vectors):
    noise = tf.random.normal([BATCH_SIZE, noise_dim]) # Controlar esto de normal o uniforme

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        generated_vectors = generator(noise, training=True)

        real_output = discriminator(vectors, training=True)
        fake_output = discriminator(generated_vectors, training=True)

        gen_loss = generator_loss(fake_output)
        disc_loss = discriminator_loss(real_output, fake_output)

    gradients_of_generator = gen_tape.gradient(
        gen_loss, generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(
        disc_loss, discriminator.trainable_variables)

    generator_optimizer.apply_gradients(
        zip(gradients_of_generator, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(
        zip(gradients_of_discriminator, discriminator.trainable_variables))

# Training process with timeout
def trainTimeout(dataset):
    spiner = Spinner("Training 'yes' GAN...")
    while(True):
        #start = time.time()
        for vector_batch in dataset:
            train_step(vector_batch)
        spiner.next()
    spiner.finish()

# Training process with EPOCHS
def trainEpochs(dataset, epochs):
    bar = IncrementalBar("Training yes GAN", max = epochs)
    for epoch in range(epochs):
        for vector_batch in dataset:
            train_step(vector_batch)        
        bar.next()
    bar.finish()


def handlerTimerGANyes(signum, frame):
    #print("Time over")
    raise Exception("Time over")

def configureTrainingYes(dataDim, dataset, pathResult, timeout):
    global train_dataset
    global dataDimension
    global cross_entropy, generator_optimizer, discriminator_optimizer
    global generator
    global discriminator
    global EPOCHS
    global noise_dim
    global BATCH_SIZE
    
    BATCH_SIZE = len(dataset)
    EPOCHS = 2000
    train_dataset = tf.data.Dataset.from_tensor_slices(dataset)
    train_dataset = train_dataset.shuffle(SHUFFLE_BUFFER_SIZE).batch(BATCH_SIZE)
    dataDimension = dataDim

    generator = make_generator_model(dataDimension)
    discriminator = make_discriminator_model(dataDimension)

    cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    generator_optimizer = tf.keras.optimizers.Adam(1e-4)
    discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

    
    noise_dim = dataDim

    if(timeout == 0):
        # Training for EPOCHS
        trainEpochs(train_dataset, EPOCHS)
    else:
        #Training for timeout
        signal.signal(signal.SIGALRM, handlerTimerGANyes)
        signal.alarm(timeout)
        try:
            trainTimeout(train_dataset)
        except Exception as e:
            print('\n')
            print_error_msj(e)
        signal.alarm(0)
    
    generator.save(pathResult + '/my_model_yes')
    print_ok_ops("Model saved")