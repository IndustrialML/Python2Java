# Tensorflow Estimator API

The `tensorflow.estimator` framework is a high level API, sitting on top of the low-level Tensorflow API. Tensorflow 1.3 currently includes the `tf.estimator` and the `tf.contrib.learn.Estimator`. Don't use the second module, as it is deprecated.  
## Building a model with Estimator
### Premade  Estimators
Tensorflow comes with a few premade, general Estimators for regression or classification problems using either a linear model or a dense neural network. You can find a guide on how to create a model with a premade Estimator [here](https://www.tensorflow.org/programmers_guide/estimators). 

I created my [Feed Forward Neural Network](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Estimator/MNISTClassifier/FFNN) for the MNIST dataset using a premade `DNNClassifier`.

### Customized  Estimators
If you are looking to build a specific NN model, these premade Estimators probably won't fit your needs. This will most likely be the case if you need more granular control over model configuration, such as 
* the ability to customize the loss function used for optimization
* or to specify different activation functions for each neural network layer
* or even to use different neural network layers, other than dense layers

In this case you will want to take a look [here](https://www.tensorflow.org/extend/estimators), this guide helps you to build your own model_fn(), which is the heart of every Estimator, defining the network layers, activation functions, the loss function and the optimizer.

I created my [Convolutional Neural Network](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Estimator/MNISTClassifier/CNN) for the MNIST dataset with a customized `Estimator`.

## Model as a Service
Now follows the interesting part, where I describe, how to save a model, which was created using an `Estimator`. As suggested in the [Tensorflow README.md](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier), we will be using Tensorflow's `SavedModel` structure, to serialize and save our trained model. 

At first I thought this was going to be pretty easy, since `Estimator` is built on top of `Tensorflow`, one would assume that I could extract the Tensorflow session and save the model in the exact same manner, as did with the low-level Tensorflow model, but sadly this is not the case. The `Estimator` framework is specifically designed to be used for serving a model with [Tensorflow Serving](https://www.tensorflow.org/serving/), which made things a bit harder than expected.

### DNNClassifier model
Saving a trained model in theory is not very hard and can be done with the following lines of code: 
```python
    #classifier = DNNClassifier(...)
    inputs = {"inputKey": tf.placeholder(shape=[None, 784], dtype=tf.float32, name="input")}
    inputReceiver = tf.estimator.export.build_raw_serving_input_receiver_fn(inputs)
    export_dir = "export"
	classifier.export_savedmodel("export_dir", serving_input_receiver_fn=inputReceiver)
```
The only thing to realy configure is the second line, defining your `inputs` variable. Here you want to specify what your model expects to be fed as input. In our case this is a batch of 784-vectors, containing the pixel informations of a batch of images. 
Notice that the `name` attribute of the input tensor(placeholder) defines the name of the tensor inside the `SavedModel`, which you can access later using `graph.get_tensor_by_name()`. On the other side, the key of the `inputs` dictionary needs to match the name of the input feature Tensor, previously defined for training and testing the model. 

The `export_savedmodel()` method creates a timestamped export directory below the given "export_dir", and writes a `SavedModel` into it. The created direcory will again consist of a "saved-model.pb" containing the `MetaGraph` of the model, and a "variables" sub-directory, containing the actual values of all variables after the training.


Now as I mentioned, this doesn't work out quite that easy, as the premade Estimators are designed to be served. When trying to export a `DNNClassifier` with a float input tensor, you will run into this error: 

>`ValueError: Classification input must be a single string Tensor; got {'inputKey': <tf.Tensor 'input:0' shape=(?, 784) dtype=float32>}`

This results from the `DNNClassifier` using a `ClassificationOutput` for saving the model. And as shown in the error message, the input for such a `ClassificationOutput` needs to be a single string Tensor, because the model expects a serialized `tf.Example` for serving. Note that this behaviour might change in future versions.

So as a workaround I created a wrapper class for a DNNCLassifier, where I replace the `export_outputs` attribute, of the created `EstimatorSpec`. Instead of a `ClassificationOutput`, I now use a general `PredictionOutput` for the export. The new `export_outputs` looks as following:
```python
export_outputs = {
                    "serving_default": tf.estimator.export.PredictOutput(
                        {"scores": tf.identity(spec.export_outputs["serving_default"].scores,"output"),
                         "class": tf.identity(spec.export_outputs["serving_default"].classes,"class")})}
```
Where `spec.export_outputs["serving_default"].scores` grabs the tensor from the original DNNClassifier, so we essentially just replaced the `ClassificationOutput` object with a `PredictOutput` object and then renamed the output tensors. 

These explicitly declared names are again important for the import of the model, so that we can later get the output vector of the probability for each number by getting the tensor by name "output", and the associated class name vector by name "class". (*Note*: for the MNIST example, the class output vector is not very useful)

Notice, how we did not pass any `signature ` to the `SavedModel`, as the `Estimator` takes care of that automatically. If we inspect the `SavedModel` using the [SavedModel CLI](https://www.tensorflow.org/programmers_guide/saved_model#cli_to_inspect_and_execute_savedmodel), we can see the connection between the signature map keys ("inputKey" , "class" , "scores"), and the tensor names ("input:0" , "class:0" , "output:0"):

> ![SavedModel CLI output picture](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Estimator/MNISTClassifier/FFNN/SavedModelCLI_example.png)


Now we have saved a regular `SavedModel` from our adjusted, premade DNNClassifier, which can be imported as usual. There is nothing that separates this `SaveModel` from a "normal" SavedModel, constructed with the low-level Tensorflow API. Just as a quick reminder, this is the way you want to re-import the model into Python:
```python
    import_super_dir = "./export/"
    timestamp=os.listdir(import_super_dir)[0]
    import_dir = import_super_dir+timestamp

    sess = tf.Session()
    graph = tf.get_default_graph()

    tf.saved_model.loader.load(sess, ["serve"], import_dir)
    y = graph.get_tensor_by_name("output:0")
    x = graph.get_tensor_by_name("input:0")
    
    #inputArray = read_array_from_input_file(...)
    prediction= sess.run(y, feed_dict={x:inputArray})

```
Since the `SavedModel` is not directly contained in the export directory, we need to grab the first (and only) sub-directory and extract the `SavedModel` into a new `session` from there. 

The full example for the DNNClassifier can be found [here](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Estimator/MNISTClassifier/FFNN).

### Customized Estimator
The workflow to save your model, built with a customized Estimator where you wrote your own `model_fn()` is just a little bit different than usual and the exporting part does not require any "plumbing"(in contrast to the DNNCLassifier), since you can define all of the `EstimatorSpec` directly on your own. 

I am going to assume that you know how to build a `model_fn()`, if that is not the case, please check my [CNN example](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Estimator/MNISTClassifier/CNN) for the MNIST dataset and the [official documentation](https://www.tensorflow.org/extend/estimators).

When constructing your `model_fn()`, you only need to make one adaption in order to being able to save your model to a `SavedModel`. You must specify the `export_outputs` element of the `tf.estimator.EstimatorSpec` return value, if the `model_fn()` is called in prediction mode. The `export_outputs` is a dictionary of {name: output} describing the output signatures to be exported, where output is any `ExportOutput`, such as `PredictOutput` or `ClassificationOutput`. As explained earlier, the `ClassificationOutput` doesn't really work for our purpose, so I am going with a `PredictOutput`:
```python
    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {"score": tf.identity(output_layer, "output")} #rename the output_layer to "output"
        export_outputs = {"serving_default": tf.estimator.export.PredictOutput(predictions)}
        return tf.estimator.EstimatorSpec(
            mode=mode,
            export_outputs=export_outputs,
            predictions=predictions
        )
```
The initialization of the classifier from your own `model_fn()` differs a bit from the initialization of a DNNClassifier, such that you don't pass in the model describing parameters, but rather your `model_fn()` and other optional parameters:
```python
    classifier = tf.estimator.Estimator(model_fn=model_fn)
```
Finally, to execute the export of the model as a `SavedModel` (after the training), you can use the same procedure as with the premade `DNNClassifier`:
```python
    inputs = {"inputKey": tf.placeholder(shape=[None, 784], dtype=tf.float32, name="input")}
    inputReceiver = tf.estimator.export.build_raw_serving_input_receiver_fn(inputs)
    export_dir="export"
    classifier.export_savedmodel(export_dir, serving_input_receiver_fn=inputReceiver)
```
Performing the import and using the model for predictions, works the same as shown above.