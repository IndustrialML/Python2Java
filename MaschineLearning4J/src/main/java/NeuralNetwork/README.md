# Neural Networks Java
In this part of the project I will describe how to use a model that was previously built, trained and exported in Python. If you have not looked at the [Python side](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork) yet, I recommend doing so.

## Model as a Service
I used two separate methods to export a Python machine learning model:
1. Keras only: Save the model into a .h5 file
2. Save the model as a Tensorflow `SavedModel`

In the [DL4J](https://github.com/Matleo/MLPython2Java/tree/develop/MaschineLearning4J/src/main/java/NeuralNetwork/DL4J) subdirectory, you will find the code to reload a previously saved Keras model with the [DL4J framework](https://deeplearning4j.org/). 

Whereas in the [Tensorflow](https://github.com/Matleo/MLPython2Java/tree/develop/MaschineLearning4J/src/main/java/NeuralNetwork/Tensorflow) subdirectory, you will find the code using the [Java Tensorflow API](https://www.tensorflow.org/api_docs/java/reference/org/tensorflow/package-summary) to import a `SavedModel`.