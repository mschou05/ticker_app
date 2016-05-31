from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import json
import datetime
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure
from bokeh.embed import components

app_schou = Flask(__name__)

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

app_schou.vars={}
app_schou.vars['stock']=''
              
@app_schou.route('/',methods= ['GET','POST'])
def index_schou():
	if request.method=='GET':
		return render_template('userinfo_schou.html')
	else:
		app_schou.vars['stock'] = request.form['stock_schou']
		return redirect('/main')	
	
@app_schou.route('/main')
def main():	
	stock = str(app_schou.vars.get('stock','')).upper()
	api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock
	session = requests.Session()
	session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
	raw_data = session.get(api_url)
	
	j=json.loads(raw_data.text)
	
	## error handle here, if no column named data
	df= pd.DataFrame(j['data'],columns=j['column_names'])
	one_m_ago = datetime.date.today() -relativedelta(months=1)
	df['DateTime'] = pd.to_datetime(df.Date)
	pastMonth =df.loc[df.DateTime>one_m_ago,['DateTime','Adj. Close']]
	
	## need error handling here: if no data
	
	plot = figure(tools=TOOLS,
              title=stock + ' Closing Price over Previous Month',
              x_axis_label='date',
              x_axis_type='datetime')
	
	plot.line(pastMonth.DateTime,pastMonth['Adj. Close'],line_width=2)
	script, div = components(plot)
	return render_template('line.html', script=script, div=div)
	
if __name__ == '__main__':
    app_schou.run(debug=False,port=33507)
    
