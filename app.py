# imports
from flask import Flask, redirect, render_template, url_for, request

import time
import os

from rq import Queue
from rq.job import Job
from worker import conn

from models import text_rank
from models.text_from_url import get_text_from_url

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

@app.errorhandler(500)
def internal_sserver_error():
    """
    Handling Internal sever error (job stays in redis for 500 seconds)
    """
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found():
    """
    Handling 404 page not found
    """
    return render_template('404.html'), 404

@app.route('/', methods = ['GET', 'POST'])
def home():
    """
    displays home page with two options (url input / text input)
    if url input -> redirects to enter_url
    if text input -> redirects to enter_text
    """
    if request.method == 'POST':
        # url input
        if 'url_input' in request.form:
            return redirect(url_for('enter_url'))

        # text input
        elif 'text_input' in request.form:
            return redirect(url_for('enter_text'))

        else:
            return render_template('index.html')

    elif request.method == 'GET':
        return render_template('index.html')

@app.route('/article_url', methods = ['GET', 'POST'])
def enter_url():
    """
    Given a url, text is retrieved from it and the summarising job is queued in redis where it is summarised, redirects to display
    """
    if request.method == 'POST':
        # getting url -> getting text
        url = request.form['url']
        text = get_text_from_url(url) # get text from url

        # redis
        q = Queue(connection=conn) # connect to redis
        job = q.enqueue(text_rank.summarize, text) # queue job
        jobid = job.get_id() # getting job id

        return redirect(url_for("display", job_id_=jobid))

    elif request.method == 'GET':
        return render_template('url_entry.html')

@app.route('/text_entry', methods = ['GET', 'POST'])
def enter_text():
    """
    Text is retrieved and the summarising job is queued in redis where it is summarised, redirects to display
    """
    if request.method == 'POST':
        # get text from forms
        text = request.form['text']

        # redis
        q = Queue(connection=conn) #connect to redis
        job = q.enqueue(text_rank.summarize, text) #queue job
        jobid = job.get_id() # getting job id

        return redirect(url_for("display", job_id_=jobid))

    elif request.method == 'GET':
        return render_template("text_entry.html")

@app.route('/display_summary', methods = ['GET', 'POST'])
def display():
    """
    Displays the selcted summary
    """
    # get job id and fetch it from redis
    jobid = request.args['job_id_']
    try:
        job = Job.fetch(jobid, connection=conn)
    except:
        return render_template("500.html")
    if request.method == 'POST':
        # get the results from the job
        full_text, sent_importance = job.result

        # getting chosen value from the dropdown
        chosen_summary_num = request.form.get('summaries')

        # getting summary
        chosen_summary = " ".join([s for s, count in zip(full_text, sent_importance) if int(count) >= int(chosen_summary_num)])

        # Time it takes to read summary, based upon number of words
        read_time = round((len(chosen_summary.split()) / 250), 2)

        # building the dropdown options
        drop_options = []
        for x in set(sent_importance):
            if x != int(chosen_summary_num):
                drop_options.append(x)
            else:
                drop_options.insert(0, x)

        # Display text on top to show what summary we are on
        if chosen_summary_num == "0":
            title_display = "Orignal"
        else:
            title_display = chosen_summary_num

        return render_template("display_summary.html", summary=chosen_summary,
                               drop_options=drop_options,
                               summary_time=read_time, title_display=title_display)

    elif request.method == 'GET':
        if job.is_finished == False:
            # if job is not over keep redirecting page to avoid session timeout
            time.sleep(15)
            return redirect(url_for("display", job_id_=jobid))

        _, sent_importance = job.result #get sent_importance (needed for the dopdown list)

        return render_template("display_summary.html",
                               summary="Choose a summary. 0 refers to the orignal text.\n Higher the number, shorter the summary.",
                               drop_options=[x for x in set(sent_importance)], summary_time=0)
if __name__ == "__main__":
    app.run(port=5000, debug=True)