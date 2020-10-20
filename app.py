from flask import Flask, redirect
from flask import render_template
from flask import url_for
from flask import request
import json

from models import text_rank
from models.text_from_url import get_text_from_url

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
    # print(request.method)
    if request.method == 'POST':
        if 'url_input' in request.form:
            return redirect(url_for('enter_url'))
        elif 'text_input' in request.form:
            return redirect(url_for('enter_text'))
        else:
            return render_template('index.html')
    elif request.method == 'GET':
        return render_template('index.html')

@app.route('/article_url', methods = ['GET', 'POST'])
def enter_url():
    if request.method == 'POST':
        url = request.form['url']
        text = get_text_from_url(url)
        summary_texts = text_rank.summarize(text)
        return redirect(url_for("display", texts=summary_texts))
    elif request.method == 'GET':
        return render_template('url_entry.html')

@app.route('/text_entry', methods = ['GET', 'POST'])
def enter_text():
    if request.method == 'POST':
        text = request.form['text']
        summary_texts = text_rank.summarize(text)
        return redirect(url_for("display", texts=summary_texts))
    elif request.method == 'GET':
        return render_template("text_entry.html")

@app.route('/display_summary', methods = ['GET', 'POST'])
def display():
    texts = json.loads(request.args['texts'])
    if request.method == 'POST':
        chosen_summary = request.form.get('summaries')
        read_time = round((len(texts[chosen_summary].split()) / 250), 2)
        return render_template("display_summary.html", summary=texts[chosen_summary],
                               drop_options=[x for x in texts.keys()], summary_time=read_time,
                               current_choice=chosen_summary)
    elif request.method == 'GET':
        return render_template("display_summary.html", summary="Choose a summary. 0 refers to the orignal text. \n Higher the number, shorter the summary.",
                               drop_options=[x for x in texts.keys()], summary_time=0)
if __name__ == "__main__":
    app.run(port=5000, debug=True)