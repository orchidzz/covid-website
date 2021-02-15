from flask import Flask, render_template, request
import plot as plt
import database
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def initialPlot():
	return render_template('index.html')


@app.route('/getdata', methods=['GET'])
def getData():
	
	if request.args.get("date"):
		date = request.args.get("date")
		
	else:
		#parse the date if needed
		date = request.args.get('year')
		month = request.args.get('month') 
		day = request.args.get('day')
		if len(month)==2:
			date += "-" + month
		else:
			date += "-0" +month
		if len(day)== 2:
			date += "-"+day
		else:
			date += "-0"+day
	
	#get data from database
	db = database.CovidDatabase()
	data = db.getRowByDate(date)
	
	#send json
	return json.dumps(data)
		
@app.route('/getplot', methods=['GET'])
def sendPlot():
	return plt.getPlot()
	


if __name__ == "__main__":
	app.run()