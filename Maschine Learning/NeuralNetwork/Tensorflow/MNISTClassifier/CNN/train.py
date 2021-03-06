import json
import tensorflow as tf
import os
import shutil
from tensorflow.examples.tutorials.mnist import input_data


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def getPredictions(Pics):
    predictions = []
    for i in range(0, 10):
        path = '../../../../Data/Own_dat/' + Pics + '-' + str(i) + '.png'
        file = tf.read_file(path)
        img = tf.image.decode_png(file, channels=1)
        resized_image = tf.image.resize_images(img, [28, 28])
        tensor = tf.reshape(resized_image, [-1])
        tArray = 1 - sess.run(tensor) / 255  # von [0,255] auf [0,1] umdrehen
        pred = determinNumber(tArray)
        predictions.append(pred)
    return predictions


def determinNumber(tArray):
    output = sess.run(tf.reshape(tArray, [1, 784]))
    guessed = sess.run(y_conv, feed_dict={x: output, keep_prob: 1})
    guessedIndex = sess.run(tf.argmax(y_conv, 1), feed_dict={x: output, keep_prob: 1})
    guessedIndex = list(guessedIndex)[0]  # um von set auf int zu kommen
    return int(guessedIndex)


def saveConfig():
    export_dir = "./export"
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    signature = tf.saved_model.signature_def_utils.build_signature_def(
        inputs={'input': tf.saved_model.utils.build_tensor_info(x),
                'dropout': tf.saved_model.utils.build_tensor_info(keep_prob)},
        outputs={'output': tf.saved_model.utils.build_tensor_info(y_conv)},
    )
    signatureMap = {
        tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature}

    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)
    builder.add_meta_graph_and_variables(sess, [tf.saved_model.tag_constants.SERVING], signature_def_map=signatureMap)
    builder.save()

    # statistics:
    diction = {}
    diction["steps"] = steps
    diction["batch_size"] = batch_size
    diction["accuracy"] = round(float(acc), 4)

    picCategories = ["Handwritten", "Computer", "MNIST", "Font"]
    picDic = {}
    for picCat in picCategories:
        predictions = getPredictions(picCat)
        picDic[picCat] = predictions
    diction["picPredictions"] = picDic
    with open("./export/statistics.json", "w") as outfile:
        json.dump(diction, outfile)

    print("\nSaved Configuration to dir: %s" % export_dir)


if __name__ == "__main__":
    save = True
    mnist = input_data.read_data_sets('../../../../Data/MNIST_data', one_hot=True)
    steps = 500
    batch_size = 50

    # Create the model
    x = tf.placeholder(tf.float32, [None, 784], name="input")

    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, 10])

    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])

    x_image = tf.reshape(x, [-1, 28, 28, 1])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    keep_prob = tf.placeholder(tf.float32, name="dropoutRate")
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
    y_conv = tf.identity(y_conv, "output")

    # Tranin the model
    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(steps):
            batch = mnist.train.next_batch(batch_size)
            # alle 100 runs ausgabe
            if i % 100 == 0:
                train_accuracy = accuracy.eval(feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
                print('step %d, training accuracy %g' % (i, train_accuracy))
            train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

        # Auswertung
        acc = accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
        print('test accuracy %g' % acc)

        if save == True:
            saveConfig()
