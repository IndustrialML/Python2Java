import os
import tensorflow as tf


def printPredictions(Pics):
    for i in range(0,10):
        path = '../../../Data/Own_dat/'+Pics+'-'+str(i)+'.png'
        file = tf.read_file(path)
        img = tf.image.decode_png(file, channels=1)
        resized_image = tf.image.resize_images(img, [28, 28])
        tensor=tf.reshape(resized_image, [-1])
        tArray=1-sess.run(tensor)/255 #von [0,255] auf [0,1] umdrehen
        determinNumber(tArray,i)


def determinNumber(tArray,i):
    output=sess.run(tf.reshape(tArray, [1,784]))
    guessed= sess.run(y, feed_dict={x:output})
    guessedIndex= sess.run(tf.argmax(y,1), feed_dict={x:output})
    guessedIndex=list(guessedIndex)[0]#um von set auf int zu kommen
    guessedProb= guessed[0][guessedIndex]*100
    print("%i: Die abgebildete Zahl ist zu %f%% eine: %d." % (i,guessedProb,guessedIndex))



if __name__ == "__main__":
    import_super_dir = "./export_ownModel/"
    timestamp=os.listdir(import_super_dir)[0] #first entry in directory
    import_dir = import_super_dir+timestamp

    sess = tf.Session()
    graph = tf.get_default_graph()

    tf.saved_model.loader.load(sess, ["serve"], import_dir)
    y = graph.get_tensor_by_name("output:0")
    x = graph.get_tensor_by_name("input:0")

    printPredictions("Handwritten")
