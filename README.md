# Going in Production with Python ML models
This project was set up by Matthias Leopold as an intern at Zuehlke Engineering AG Schlieren, to gather the options to use a trained Python machine learning model for production.

## Project structure
The project is split into two sub-projects: 
1. [Machine Learning (Python part)](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning)
2. [Machine Learning 4J (Java part)](https://github.com/Matleo/MLPython2Java/tree/develop/MaschineLearning4J)

Each sub-project itself is ordered by model type. The following models were considered *(links go to the Python part)*:
* [Artificial Neural Networks](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork)
* [Random Forest](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/RandomForest)

In general, two separate approaches were evaluated:
1. **Model as a Service**: The whole ML model is supposed to be transfered from Python to Java, to execute predictions directly in Java
2. **Inference as a Service**: The ML model is supposed to be deployed from Python and an inference service is supposed to be made available

## Getting started
I will briefly show you how to get one of the Neural Network experiments started, assuming you have cloned this repository and installed Java, Maven, Python and Pip already.
1. Set up your Python environment (might be done in a `virtualenv`): 
```bash
	pip install tensorflow keras flask
```
2. Build your Java project with Maven, using the dependencies from this [pom.xml](https://github.com/Matleo/MLPython2Java/blob/develop/MaschineLearning4J/pom.xml)

### Model as a Service
To get started with using a pretrained machine learning model from Python in Java, you can follow this workflow:
1. Decide which model you want to use. For this example I will use the [Feed Forward Neural Network](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel) trained with Tensorflow.
2. *optional*: Retrain the model. As every model has been initially trained and saved, this step is optional. You can train (and export) the model by simply executing the [train.py](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel/train.py) script of your model. 
3. Run the [test.py](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Tensorflow/MNISTClassifier/Feed%20Forward%20NN/SavedModel/test.py) script, which will load the saved model and make prediction against 10 saved .png files in the [data](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/Data/Own_dat) folder. The output should look something like this: 
	```python
	0: The given picture is a 0 with probability of: 100.000000%.
	1: The given picture is a 1 with probability of: 99.997020%.
	2: The given picture is a 2 with probability of: 99.762875%.
	3: The given picture is a 3 with probability of: 100.000000%.
	4: The given picture is a 4 with probability of: 99.993777%.
	5: The given picture is a 5 with probability of: 99.921405%.
	6: The given picture is a 6 with probability of: 84.739697%.
	7: The given picture is a 7 with probability of: 100.000000%.
	8: The given picture is a 8 with probability of: 99.999917%.
	9: The given picture is a 9 with probability of: 99.999940%.
	```
4. Now that everything runs in Python as it should, we can start using the saved model for predictions in Java. For that you can run the execution class [MNISTClassifier](https://github.com/Matleo/MLPython2Java/blob/develop/MaschineLearning4J/src/main/java/NeuralNetwork/Tensorflow/MNIST/MNISTClassifier.java). If you don't pass any program arguments, it will load the saved model from the Tensorflow Feed Forward Neural Network, calculate the accuracy of the model with the MNIST dataset, classify a few previously saved .png files from the [data](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/Data/Own_dat) folder and compare the results against the Python results. If everything worked correctly, the tail of the output will look something like:
	```java
	Comparing Java and Python results:
	***Success***
		The calculated accuracy on the MNIST dataset in Java and Python match!
	***Success***
		The Python and Java predictions match!

	The import of the model was successfully completed!
    ```
	For more information on how to use this program, please pass in `-h` as program parameter or refer to the [README](https://github.com/Matleo/MLPython2Java/tree/develop/MaschineLearning4J/src/main/java/NeuralNetwork/Tensorflow) 

### Inference as a Service
The following workflow will show how to serve a pretrained neural network model and use it to provide a RESTful API:
1. Decide which model you want to use and pass it as script parameter to the [flask application](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Serving/Flask_Serving.py) like this: `--model <value>`. The `<value>` parameter can be any of: `t_ffnn` / `t_cnn` / `e_ffnn` / `e_cnn` / `k_ffnn` / `k_cnn`, where for example `t_ffnn` will load the feed forward neural network that was trained with Tensorflow. `t_ffnn` will be the default value if you do not pass any.
2. Run the [flask application](https://github.com/Matleo/MLPython2Java/blob/develop/Maschine%20Learning/NeuralNetwork/Serving/Flask_Serving.py), to provide a RESTful API locally on port 8000. 
3. Make a request to the API by sending a 2-dimensional integer array, representing a grayscale image. You can use the [InferenceClient](https://github.com/Matleo/MLPython2Java/blob/develop/MaschineLearning4J/src/main/java/InferenceClient.java) Java application for sending such a request. Pass in an absolute path to a .png or the filename of a .png contained in the [Data/Own_dat](https://github.com/Matleo/MLPython2Java/tree/develop/Maschine%20Learning/Data/Own_dat) folder, as program argument. If no program argument is passed, the prediction will be done with a default picture.

## Prerequisites
* Python 3.6.2
	* Flask 0.12.2
	* Keras 2.0.8
	* Opencv-python 3.3.0.10
	* Pip 9.0.1
	* Scikit-learn 0.19.0
	* Sklearn2pmml 0.26.0
	* Tensorflow 1.3
* Java 1.8
	* Apache httpclient 4.5.2
	* Google's json-simple 1.1.1
	* Maven 3.5.0
	* Pmml-evaluator 1.3.9
	* Tensorflow 1.3.0
	* Thumbnailator 0.4.8