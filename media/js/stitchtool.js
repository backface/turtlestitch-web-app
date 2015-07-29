
	var showStitches = false;
	var pathColor = "black";
	var jumpColor = "white";
	var endColor = "red";
	var dragColor = "black";
	var mouseDownColor = "black";
	
	var baseUrl=getBaseURL()
	var myStitches = []
	var jump=false;
	var jumpEnds = [];
	var jumpPaths = [];
	var myPath = new Path();
	var points = [];
	var ptypes = [];	
	var len;
	var myEnd = new Path.Circle();	
	
	myEnd.strokeColor = endColor;
	tool.fixedDistance = 5;

	function onMouseDown(event) {

		myPath.strokeColor = mouseDownColor;
		myPath.add(event.point);
		points.push(event.point);
		ptypes.push(jump);
		if (showStitches) {
			st = new Path.Circle(event.point,1)
			st.strokeColor = pathColor;
			myStitches.push(st);
		}
		if (jump) {
			j = new Path.Circle(event.point,1);
			j.strokeColor = jumpColor;
			jumpEnds.push(j);
			jumpPaths[jumpPaths.length-1].add(event.point);
			jump = false;
		}
		myEnd.removeOnUp();
	}

	
	function onMouseUp(event) {
		myPath.strokeColor = pathColor;
		myEnd = new Path.Circle(new Point(points[points.length-1].x, points[points.length-1].y),2);
		myEnd.strokeColor = endColor;
	}
		
	function onMouseDrag(event) {
		myPath.strokeColor = dragColor;
		myPath.add(event.point);
		points.push(event.point);
		ptypes.push(jump);
		if (showStitches) {
			st = new Path.Circle(event.point,1)
			st.strokeColor = pathColor;
			myStitches.push(st);
		}
		if (jump) {
			j = new Path.Circle(event.point,1);
			j.strokeColor = jumpColor;
			jumpEnds.push(j);
			jumpPaths[jumpPaths.length-1].add(event.point);
			jump = false;
		}		
	}	
	
	function onKeyDown(event) {
		if (event.key == 'j') {
			jump = true;
			var p = new Point(points[points.length-1].x, points[points.length-1].y);
			var j = new Path.Circle(p,1);
			j.strokeColor = jumpColor;
			jumpEnds.push(j);
			var jp = new Path();
			jp.add(p);
			jp.strokeColor = jumpColor;
			jumpPaths.push(jp);
		}
	}	

	function clear() {
		points = [];
		ptypes = [];
		myPath.removeSegments();
		myEnd.remove();

		for (i=0;i<jumpEnds.length;i++) {
			jumpEnds[i].remove();
		}	
		for (i=0;i<jumpPaths.length;i++) {
			jumpPaths[i].removeSegments();
		}
		if (showStitches) {
			for (i=0;i<myStitches.length;i++) {
				myStitches[i].remove();
			}
			myStitches = [];
		}	
		
		jumpEnds = [];
		jumpPaths = [];
		jump = false;
		
		$("#result").html("");
	}
	
	function back() {

		if (ptypes[ptypes.length-1] == true) {
			jumpPaths[jumpPaths.length-1].removeSegments();
			jumpPaths.pop();
			jumpEnds[jumpEnds.length-1].remove();
			jumpEnds.pop();
			jumpEnds[jumpEnds.length-1].remove();
			jumpEnds.pop();
		}
		myPath.removeSegment(myPath._segments.length-1);
		if (showStitches) {
			myStitches[myStitches.length-1].remove();
			myStitches.pop();
		}
		points.pop();
		ptypes.pop();
		
		myEnd.remove();
		myEnd = new Path.Circle(new Point(points[points.length-1].x, points[points.length-1].y),2);
		myEnd.strokeColor = endColor;		
		
		$("#result").html("");
	}

	function back10() {
		len=myPath._segments.length;
		if (len > 10 ) {
			myPath.removeSegments(len-10);
			$("#result").html("");
			for(i=0;i<10;i++) {
				if (ptypes[ptypes.length-1] == true) {
					jumpPaths[jumpPaths.length-1].removeSegments();
					jumpPaths.pop();
					jumpEnds[jumpEnds.length-1].remove();
					jumpEnds.pop();
					jumpEnds[jumpEnds.length-1].remove();
					jumpEnds.pop();
				}			  
				if (showStitches) {
					myStitches[myStitches.length-1].remove();
					myStitches.pop();
				}			  
				points.pop();
				ptypes.pop();
			}
		}  

		myEnd.remove();
		myEnd = new Path.Circle(new Point(points[points.length-1].x, points[points.length-1].y),2);
		myEnd.strokeColor = endColor;
				
	}
	
	function send() {
		params = { "points[]": points, "ptypes[]":ptypes };				
		$.fileDownload(baseUrl+"save.py", {
			successCallback: function (html, url) {
			},
			failCallback: function (html, url) {
				alert(
				  'Your file download just failed for this URL:' + url + 
				  '\r\n' + 'Here was the resulting error HTML: \r\n' 
					+ html
				);
			},
		
			httpMethod: "POST",
			data: params
		});	
	}
	
	$('#send').click (function() { send(); });
	$('#clear').click (function() { clear(); });
	$('#back').click (function() { back(); });
	$('#back10').click (function() { back10(); });
	
