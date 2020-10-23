from flask import Flask, redirect
from flask import render_template
from flask import url_for
from flask import request, session
import time

from rq import Queue
from rq.job import Job
from worker import conn

from models import text_rank
from models.text_from_url import get_text_from_url

app = Flask(__name__)
app.secret_key = "ANISH"

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

        q = Queue(connection=conn)
        job = q.enqueue(text_rank.summarize, text)
        session["job_id"] = job.get_id()

        return redirect(url_for("display"))
    elif request.method == 'GET':
        return render_template('url_entry.html')

@app.route('/text_entry', methods = ['GET', 'POST'])
def enter_text():
    if request.method == 'POST':
        text = request.form['text']

        q = Queue(connection=conn)
        job = q.enqueue(text_rank.summarize, text)
        session["job_id"] = job.get_id()

        return redirect(url_for("display"))

    elif request.method == 'GET':
        return render_template("text_entry.html")

@app.route('/display_summary', methods = ['GET', 'POST'])
def display():
    job = Job.fetch(session["job_id"], connection=conn)

    if request.method == 'POST':
        full_text, sent_importance = job.result

        chosen_summary_num = request.form.get('summaries')
        chosen_summary = " ".join([s for s, count in zip(full_text, sent_importance) if int(count) >= int(chosen_summary_num)])
        read_time = round((len(chosen_summary.split()) / 250), 2)

        drop_options = []
        for x in set(sent_importance):
            if x != int(chosen_summary_num):
                drop_options.append(x)
            else:
                drop_options.insert(0, x)

        if chosen_summary_num == "0":
            title_display = "Orignal"
        else:
            title_display = chosen_summary_num

        return render_template("display_summary.html", summary=chosen_summary,
                               drop_options=drop_options,
                               summary_time=read_time, title_display=title_display)
    elif request.method == 'GET':
        if job.is_finished == False:
            time.sleep(5)
            return redirect(url_for("display"))
        _, sent_importance = job.result
        return render_template("display_summary.html", summary="Choose a summary. 0 refers to the orignal text. \n Higher the number, shorter the summary.",
                               drop_options=[x for x in set(sent_importance)], summary_time=0, job=job)
if __name__ == "__main__":
    app.run(port=5000, debug=True)