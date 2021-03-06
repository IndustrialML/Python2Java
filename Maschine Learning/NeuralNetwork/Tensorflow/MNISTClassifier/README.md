# Low level Tensorflow API
I worked with Tensorflow version 1.3, the full documentation can be found [here](https://www.tensorflow.org/api_docs/).

I am going to focus on describing the workflow to save a Tensorflow model, rather than explaining how to build and train one. If you are looking for an introduction on the MNIST dataset and Tensorflow in general, you might want to read [Tensorflow getting started](https://www.tensorflow.org/get_started/mnist/beginners) and take a look at my commented code [here](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/saver/train.py).


## Model as a Service
### Saver
Firstly I tried to save the trained model in a format, so that it can be saved to a file and re-imported into Python later. This was easily accomplished by using the `tensorflow.train.Saver()`. 
#### Export
The important code snippet from the [export code](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/saver/train.py) is this:
```python
    x = tf.placeholder(tf.float32, [None, 784], name="input")
    dKeep = tf.placeholder(tf.float32, name="dropoutRate")
    #build some layers...
    y3 = tf.nn.softmax(tf.matmul(y2, W3) + b3)
    y3 = tf.identity(y3, "output")

    sess = tf.Session()
    #train the model...
    export_dir = "./export/model"
    saver = tf.train.Saver()
    saver.save(sess, export_dir)
```
The `saver.save()` creates multiple files in the sub directory "export" with the name "model".xxx. 

I explicitly showed how to create the input tensors `x` and `dKeep` and the output tensor `y3`, because we will need the names of these tensors later for the import. Note that the name of the output tensor can only be set, by recreating the tensor with a different name, using `tf.identity()`. Since the input tensors are `tf.placeholder`s, we can directly pass a name as a parameter.

#### Import
The model, with all its weights and biases, can then be loaded into a newly created session:
```python
    sess = tf.Session()
    import_dir = "./export/model"
    saver = tf.train.import_meta_graph(import_dir + ".meta")
    saver.restore(sess, import_dir)
```
Here, at first the model structure is loaded into the saver object, calling `tf.train.import_meta_graph()` on the "model.meta" file, before the model with its weights and biases is loaded into the new session with `saver.restore()`.

To be able to make predictions with the imported model, you will need to grab the input and output tensors from the model, in order to feed/fetch values:
```python
    graph = tf.get_default_graph()
    y3 = graph.get_tensor_by_name("output:0")
    x = graph.get_tensor_by_name("input:0")
    dKeep = graph.get_tensor_by_name("dropoutRate:0")
    
    #actual prediction call (the "inputArray" is an array, read from a .png file):
    prediction = sess.run(y3, feed_dict={x: inputArray, dKeep: 1})

```
The `tf.get_default_graph()` gets the actual graph of the imported session. Important to notice is that the names of the tensors need to match the names of the originally exported model (which are shown above). 

For more information you can see the example of the [import code](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/saver/test.py) and the full documentation of the [Tensorflow Saver](https://www.tensorflow.org/api_docs/python/tf/train/Saver#restore). 

### SavedModel
Saving and reloading a model in python can be very useful, but what we want to achieve, is to export a model into a format that is somewhat platform independent, in order to import it into a Java environment and to be able to use the model to make predictions, without the need to run python code.

For any Tensorflow model, this is achievable with the `tf.saved_model` class. And as you will notice later, saving an Estimator or Keras model is going to be based on *SavedModel* aswell. 

The model used for this example is the same as in the example for the `tensorflow.train.Saver()`. So the only thing to change here, is how to export and import the trained model. Additionally we will now be able to import the model into Java aswell, using the [Tensorflow Java API](https://www.tensorflow.org/api_docs/java/reference/org/tensorflow/package-summary).

#### Export
All the work happens in these few lines of code ([see full example](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel/train.py)):
```python
    sess = tf.InteractiveSession()

    #build and train model...

    export_dir = "./export"
    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)
    builder.add_meta_graph_and_variables(sess, 
            [tf.saved_model.tag_constants.SERVING])
    builder.save()
```
Inside the "export" directory  will be a "saved_model.pb" file containing the meta graph of the model, and a "variable" sub-directory, containing all variables. 

Often it is advisable to add a Signature to the SavedModel, describing the set of inputs and outputs from a model:
```python
    signature = tf.saved_model.signature_def_utils.build_signature_def(
        inputs={'input': tf.saved_model.utils.build_tensor_info(x),
                'dropout': tf.saved_model.utils.build_tensor_info(dKeep)},
        outputs={'output': tf.saved_model.utils.build_tensor_info(y3)},
    )
    signatureMap = { tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature }

    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)
    builder.add_meta_graph_and_variables(sess, 
		[tf.saved_model.tag_constants.SERVING], 
		signature_def_map=signatureMap)
    builder.save()
```
This signature can then be inspected, using the [SavedModel CLI](https://www.tensorflow.org/programmers_guide/saved_model#cli_to_inspect_and_execute_savedmodel). For our SavedModel, the output can look as following: 

> ![Image of SavedModel CLI Output](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel/SavedModelCLI_example.png)

**Note:** I am additionally saving some statistics in separate json files for each of my examples (accuracy against MNSIT test set and predictions for some downloaded pictures). These statistics will later be used for validating the Java results and to see, if the predictions from both technologies match.

#### Import
In the following, I will shortly describe, how to import a SavedModel into Python, for the Java part, please refer to [here](https://github.com/Matleo/MLPython2Java/tree/develop/MaschineLearning4J/src/main/java/NeuralNetwork/Tensorflow).

The import is almost identical to what we did with `tensorflow.train.Saver()`, only one line of code is new:
```python
    import_dir = "./export"
    sess = tf.Session()
    tf.saved_model.loader.load(sess, ["serve"], import_dir)
```

Afterwards you can grab the input and output tensors from the session, like before, and start making predictions without having to train the model again. The full code can be viewed [here](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel/test.py).

You can apply the workflow to any model you like. For validation purpose, I tried saving and reloading a Convolutional Neural Network for the same MNIST example. The only thing to change was how to build the model. You can view the CNN example [here](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/CNN)

For more information, please refer to the [official documentation](https://www.tensorflow.org/programmers_guide/saved_model#apis_to_build_and_load_a_savedmodel)