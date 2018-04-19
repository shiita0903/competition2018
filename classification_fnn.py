# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A very simple MNIST classifier.
See extensive documentation at
https://www.tensorflow.org/get_started/mnist/beginners
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

from tensorflow.examples.tutorials.mnist import input_data
from competition_utility import dafaset_loader as dl

import tensorflow as tf

FLAGS = None


def main(_):
  # Import data
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

  dirs = ["Images", "OTHERS"]
  labels = [dl.DataSet.TARGET, dl.DataSet.OTHERS]
  loader = dl.DatasetLoader(dirs, labels)
  train, test = loader.load_train_test()
  train.print_information()
  test.print_information()

  # Create the model
  x = tf.placeholder(tf.float32, [None, 64*64*3])
  W = tf.Variable(tf.zeros([64*64*3, 2000]))
  b = tf.Variable(tf.zeros([2000]))
  h = tf.nn.sigmoid(tf.matmul(x, W) + b)

  W2 = tf.Variable(tf.zeros([2000, 2]))
  b2 = tf.Variable(tf.zeros([2]))
  y = tf.nn.softmax(tf.matmul(h, W2) + b2)

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 2])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
  # outputs of 'y', and then average across the batch.
  cross_entropy = tf.reduce_mean(
      tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
  train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)

  sess = tf.InteractiveSession()
  tf.global_variables_initializer().run()
  # Train
  for _ in range(1000):
      for image in train():
        batch_xs, batch_ys = image.images, image.labels
        batch_xs = batch_xs.reshape((len(batch_xs), 64*64*3))

        sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
      if _ % 10 == 0:
        print("Train", sess.run(cross_entropy, feed_dict={x: batch_xs, y_: batch_ys}))
        print("Test", sess.run(cross_entropy, feed_dict={x: test.images.reshape((test.images.shape[0], 64*64*3)), y_: test.labels}))

  # Test trained model
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  print(sess.run(accuracy, feed_dict={x: test.images.reshape((len(test.images), 64*64*3)),
                                      y_: test.labels}))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='/tmp/tensorflow/mnist/input_data',
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)