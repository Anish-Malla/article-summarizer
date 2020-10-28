# Article Summarizer

![GitHub repo size](https://img.shields.io/github/repo-size/Anish-Malla/article-summarizer)
![GitHub contributors](https://img.shields.io/github/contributors/Anish-Malla/article-summarizer)

### <em>Summarize Articles, Save Time</em>

Article Summarizer is an application which allows user to summarise an article.

The user can input an article as plain text or they can input the URL of the article. Given an article this application extracts
the key sentences from the article and returns one or more summaries.

## Website

This application is hosted on heroku:

https://article-summarizer-anish.herokuapp.com/

## How to run the app locally

**Requirements:** python-3.8.6

* Clone the GitHub repo
```
git clone https://github.com/Anish-Malla/article-summarizer
```
* Install required libraries
```
pip3 install -r requirements.txt
```
* Run a redis server locally
```
Instruction to run redis server: https://redis.io/topics/quickstart
``` 
* Running worker process for redis (On a new terminal)
```
python3 worker.py
```
* Run the flask application on http://localhost:5000/ (On a new terminal)
```
python3 app.py
```

## How it works

1. Getting the article's text (comes from URL or text inputted by user)
2. This text is ran through an extractive graph based summariser
3. The summariser ranks the sentences based upon importance and the result is outputted to the user

## Contributors

* [@AnishMalla](https://github.com/scottydocs) 