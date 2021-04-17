# Sentiment Analysis Chat Application
Deployed at: https://sachatml.appspot.com/

## Overview

Sentiment analysis chat application runs between a user, **Naive Bayes Bot**, and a **Deep Neural Net Bot** to predict a sentiment score from 0 (negative) to 4 (positive) each time the user sends a message.

**NOTE:** API calls currently return a random number between 0 and 4 until implemented. 

### Development Quick Start

---

- ```cd``` to ```/api/``` and optionally create a local virtual environment by running ```python3 -m venv env```

- Then, resolve the Python ML server dependencies by running ```pip3 install -r requirements.txt```

- ```cd``` to ```/react_frontend/``` and resolve JS ```package.json``` dependencies by running ```npm install```

- From one terminal run ```yarn start-api```

- From another terminal run ```yarn start```


## ML Prediction Server REST API Documentation

Messages sent by the user are translated into HTTP requests to the ML Prediction server at the following endpoints:

```[POST] /api/predict/NaiveBayes```

```[POST] /api/predict/DeepNeuralNet```

**Example Request:**

```HTTP POST https://SAChatML.appspot.com/api/predict/NaiveBayes```

```json
{
	"Message": "Include the message to run sentiment analysis on here"
}
```

Each endpoint will load its pretrained ML model and:

- Run a prediction on the message specified by the request

- Serve a response containing the predicted sentiment score

### Request Formating

---

**HTTP POST** requests to the ML prediction server provide the following:

```json
headers:
{
	"Content-type": "application/json"
}
```

```json
body:
{
	"Message": "Today was such a great day, it was awesome and the best time I have ever had!"
}
```

The request body should specify a JSON with the single attribute **Message** containing the message to run sentiment prediction on.

### Response Formating

---

**HTTP POST** requests to the ML prediction server will receive a reponse similar to the following body:

```json
{
	"Score" : 4
}
```

Where the response will contain a single **Score** attribute JSON with a value **between 0 and 4**.