from flask import Flask, render_template, request, redirect
from datetime import date, timedelta
import os
import requests
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Legend
from bokeh.models.widgets import PreText, Select
from bokeh.embed import components

# --- Set up Flask ---
app  = Flask(__name__)
app.debug = True
app.vars={}
api_key = os.environ.get('QUANDL_KEY')

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == 'GET':
	#provide index with input form
	return render_template('index.html')
    else:
	#request was POST, provide graph
	app.vars['tickerinput'] = request.form['tickersym']
    return redirect('/graph')

@app.route('/graph')
def graph():
    # --- Get Quandl data ---
    # get date of one month ago
    t1 = str(date.today() - timedelta(30))
    # request data from quandl using ticker input and date
    url = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=%s&date.gte=%s&api_key=%s" % (app.vars['tickerinput'], t1, api_key)
    r = requests.get(url)
    #create dataframe in pandas
    cols = [x["name"] for x in (r.json()['datatable']['columns'])]
    data = pd.DataFrame((r.json()['datatable']['data']), columns=cols)
    data['date'] = pd.to_datetime(data['date'])
    # --- Create graph ---
    p = figure(plot_width=500, plot_height=400, x_axis_type='datetime')
    p.line(x=data['date'], y=data['open'], color='lightblue', line_dash='dashed', legend='Opening Price')
    p.line(x=data['date'], y=data['close'], color='darkblue', legend='Closing Price')
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    script, div = components(p)
    return render_template('graph.html', script=script, div=div, tickersym=app.vars['tickerinput'])
    

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
