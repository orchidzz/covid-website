$('document').ready(function(){
	
	//return covid info from database after sending date to server by submitting form
	$('#date').submit(function(){
		var day = $('#day').val().toString();
		var month = $('#month').val().toString();
		var year = $('#year').val().toString();
		$.ajax({
			url: '/getdata',
			type: 'GET',
			datatype: 'json',
			data: {'day': day, 'month': month, 'year': year},
			success: function(response){
				var result = $.parseJSON(response);
				
				//catch error when result is null
				if (result == null){
					$('#cases-output').text("");
					$('#deaths-output').text("");
					$('#recovered-output').text("");
				}else{
					$('#cases-output').text(result.cases);
					$('#deaths-output').text(result.deaths);
					$('#recovered-output').text(result.recovered);
				}
			}
	
		});
	});
	
	//embed mpld3 plot into website
	$.ajax({
		url: '/getplot',
		type: 'GET',
		success: function(response){
			mpld3.draw_figure("plot-fig", $.parseJSON(response));
			
			//$("g.mpld3-baseaxes").css("transform", "translate:(150px, 0px)");
		}
	});
});

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
	
	//date var in order to show on plot
	var date;
	
	//create element for textbox
	var textbox = fig.canvas.append("text").attr("class", "textbox").style("width", "60px").style("height","35px").style("font-size", "30px").style("fill", "orange");
    
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
				hori_line.attr("y1", pos[1]);
				hori_line.attr("x2", fig.width);
				hori_line.attr("y2", pos[1]);
				
				//draw vert line over plot based on mouse position
				vert_line.attr("x1", pos[0]+150);
				vert_line.attr("y1", 0);
				vert_line.attr("x2", pos[0]+150);
				vert_line.attr("y2", fig.height);
				
				//show lines when mouse inside plot
				hori_line.style("display","block");
				vert_line.style("display", "block");
				
				//update date variable whenever mouse moves
				date = xfmt(x);
				
				//display textbox showing the date whenever hover over the plot
				textbox.attr("x", pos[0]+150);
				textbox.attr("y", pos[1]);
				textbox.text(xfmt(x));
			};
			
		}();
		
		//control mouse events
		fig.axes[i].baseaxes.on("mousemove", update_coords).on("mouseover", update_coords).on("mousedown", function(){
			//send request for covid info based on clicked date when clicking on date
			$.ajax({
				url: '/getdata',
				type: 'GET',
				datatype: 'json',
				data: {'date': date.toString()},
				success: function(response){
					//parse the json result
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
			})
		}).on("mouseout", function() {
			//hide coords and textbox displaying date when mouse outside of plot
			coords.text("");
			textbox.text("");
			
			//hide lines when mouse outside of plot
			hori_line.style("display", "none");
			vert_line.style("display", "none");
		});
    }
	
};