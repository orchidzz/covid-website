import matplotlib
#change backend server so that the plot won't be produced outside the main thread
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import mpld3
import json
import database

class CovidPlotPlugin(mpld3.plugins.PluginBase):
    '''modified plugin for displaying mouse position with a datetime x axis, drawing vert and horizontal lines over graph at position of mouse, showing covid info based on clicked date, displaying date on hover, translating the plot'''
	
    JAVASCRIPT = '''
    //modified mpld3 plugin 
	mpld3.register_plugin("covidplotplugin", CovidPlotPlugin);
	CovidPlotPlugin.prototype = Object.create(mpld3.Plugin.prototype);
	CovidPlotPlugin.prototype.constructor = CovidPlotPlugin;
	CovidPlotPlugin.prototype.requiredProps = [];
	CovidPlotPlugin.prototype.defaultProps = {
		fontsize: 12,
		xfmt: "%Y-%m-%d",
		yfmt: ".3g"
		};
	function CovidPlotPlugin(fig, props) {
		mpld3.Plugin.call(this, fig, props);
	}
	CovidPlotPlugin.prototype.draw = function() {
		var fig = this.fig;
		var xfmt = d3.time.format(this.props.xfmt);
		var yfmt = d3.format(this.props.yfmt);
    
		//create element to show coords at bottom right
		var coords = fig.canvas.append("text").attr("class", "mpld3-coordinates").style("text-anchor", "end").style("font-size", this.props.fontsize).attr("x", this.fig.width - 5).attr("y", this.fig.height - 5);
	
		//create elements for lines over graph.
		var hori_line = fig.canvas.append("line").attr("class", "hori-line").style("stroke", "gray");
		var vert_line = fig.canvas.append("line").attr("class", "vert-line").style("stroke", "gray");
	
		//create element for textbox
		var textbox = fig.canvas.append("text").attr("class", "textbox").style("width", "60px").style("height","35px").style("font-size", "30px").style("fill", "orange");
		
		var date;
    
		const x_offset = fig.axes[0].position[0];
		const y_offset = fig.axes[0].position[1];
		
		//translate the plot to (150,0)
		fig.canvas.select(".mpld3-baseaxes").style("transform", "translate(150px, 0px)");
		
		for (var i = 0; i < this.fig.axes.length; i++) {
			var update_coords = function() {
				var ax = fig.axes[i];
			
				return function() {
					//get position of mouse
					var pos = d3.mouse(this);
				
					//get dates (x coord), and number(y coord) using position of mouse
					x = ax.xdom.invert(pos[0]);
					y = ax.ydom.invert(pos[1]);
				
					//show the coords text at bottom right
					coords.text("(" + xfmt(x) + ", " + yfmt(y) + ")");
			
					//draw hori line over plot based on mouse position
					hori_line.attr("x1", 0);
					hori_line.attr("y1", pos[1]+y_offset);
					hori_line.attr("x2", fig.width);
					hori_line.attr("y2", pos[1]+y_offset);
				
					//draw vert line over plot based on mouse position
					vert_line.attr("x1", pos[0]+x_offset);
					vert_line.attr("y1", 0);
					vert_line.attr("x2", pos[0]+x_offset);
					vert_line.attr("y2", fig.height);
				
					//show lines when mouse inside plot
					hori_line.style("display","block");
					vert_line.style("display", "block");
				
					//update date variable whenever mouse moves
					date = xfmt(x);
					
					//display textbox showing the date whenever hover over the plot
					textbox.attr("x", pos[0]+x_offset);
					textbox.attr("y", pos[1]+y_offset);
					textbox.text(xfmt(x));
				};
			
			}();
		
			//mouse events
			fig.axes[i].baseaxes.on("mousemove", update_coords).on("mouseover", update_coords).on("mouseout", function() {
				//hide coords and textbox when mouse outside of plot
				coords.text("");
				textbox.text("");
			
				//hide lines when mouse outside of plot
				hori_line.style("display", "none");
				vert_line.style("display", "none");
			}).on("mousedown", function(){
				//send request for covid info based on clicked date
				$.ajax({
					url: '/getdata',
					type: 'GET',
					datatype: 'json',
					data: {'date': date.toString()},
					success: function(response){
						var result = $.parseJSON(response);
					
						//if the result is null, catch error by returning null
						if (result==null){
							return;
						}else{
							//update elements if result is not null
							$('#cases-output').text(result.cases);
							$('#deaths-output').text(result.deaths);
							$('#recovered-output').text(result.recovered);
						}
					}
				});
			});
		}
	};
    '''
	
    def __init__(self, fontsize=14, xfmt="%Y-%m-%d", yfmt=".0f"):
        self.dict_ = {"type": "covidplotplugin","fontsize": fontsize,"xfmt": xfmt,"yfmt": yfmt}
		
#output json of matplotlib
def getPlot():
	#get data make it into dataframe
	db = database.CovidDatabase()
	data = db.getAllFromTable()
	df = pd.DataFrame(data, columns=['date', 'cases', 'recovered', 'deaths'])
	df = df.sort_values(by='date',ascending=True)
	
	#set up axes
	ax = plt.gca()
	#ax.tick_params(axis="both", colors="white")
	#ax.grid(color="lightgray")
	
	#format the x axis
	plt.ticklabel_format(style='plain')
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
	
	#plot the data
	fig1 = plt.plot('date','cases', marker= '.', data=df, color='yellow', ms = 5, linewidth=0.5)
	fig2 = plt.plot('date','recovered', marker = '.',data=df, color='green', ms=5, linewidth=0.5)
	fig3 = plt.plot('date','deaths', marker = '.', data=df, color='red', ms=5, linewidth=0.5)
	
	
	#get current figure to output json
	figure = plt.gcf()
	plt.tight_layout()
	
	#set plot's height and width based on size of data
	x_size = len(df.index)
	y_size = df["cases"][x_size-1]
	figure.set_figheight(y_size//14576634)
	figure.set_figwidth(x_size*0.08)
	
	#set background color of plot
	ax.patch.set_facecolor("black")
	mpld3.plugins.connect(figure, CovidPlotPlugin())
	
	plt.close()
	return json.dumps(mpld3.fig_to_dict(figure))

