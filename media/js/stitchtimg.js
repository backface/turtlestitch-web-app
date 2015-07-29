

	var showStitches = false;
	//var pathColor = "black";
	var pathColor = "red";
	var jumpColor = "white";
	var endColor = "red";
	var dragColor = "red";
	//var dragColor = "black";
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
	var logtxt = ""
	var raster;
	
	myEnd.strokeColor = endColor;
	tool.fixedDistance = 5;


	function log(str) {
		console.error(str);
		logtxt += str;
		//$("#debug").html("<pre>" + logtxt + "</pre>");
		//alert($("#debug").html);
	}


	function onMouseDown(event) {
		
		//alert("Maus runter");
		project.activeLayer.addChild(myPath);
		myPath.strokeColor = mouseDownColor;
		myPath.add(event.point);
		points.push(event.point);
		ptypes.push(jump);
		log("new point" + event.point + " num points= " + points.length + " num ptypes= "  + ptypes.length);
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
		log("new point" + event.point + " num points= " + points.length + " num ptypes= " + ptypes.length);
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
			log("next is jump");
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
		
		logtxt = "";
		
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
		name = $("#name").val();
		params = { "points[]": points, "ptypes[]":ptypes, name:name };		
		log("sending SAVE with num points= " + points.length + " num ptypes= " + ptypes.length);		

/*		$.fileDownload(baseUrl+"/draw/upload", {
			successCallback: function (html, url) {
				alert(html);
				window.open('http://' + window.location.hostname + '/draw/view/'+data, 'TurtleStitch file preview');
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
		});	*/
		
		$.post(baseUrl+"/draw/upload", data = params,
			function (data) {
				if (data.slice(0,2) == "OK") {
					fid = data.slice(3);
					window.open('http://' + window.location.hostname + '/draw/view/'+fid, 'Drawtool file preview');
				} else {
					alert(
					  'Your file upload just failed for this URL:' + url + 
					  '\r\n' + 'Here was the resulting error HTML: \r\n' 
						+ data);					
				}
			});
	}

	function onDocumentDrag(event) {
		event.preventDefault();
	}

	function onDocumentDrop(event) {
		event.preventDefault();

		var file = event.originalEvent.dataTransfer.files[0];
		var reader = new FileReader();

		reader.onload = function (event) {
			project.activeLayer.removeChildren();
			raster = new Raster();
			raster.source = event.target.result;
			raster.position = view.center;
			log("raster bounds: " + raster.bounds);
			log("raster width: " + raster.bounds.width);
			log("raster height: " + raster.bounds.height);
			raster.scale(0.77);			
		};
		reader.readAsDataURL(file);
	}

	$(document).on({
		drop: onDocumentDrop,
		dragover: onDocumentDrag,
		dragleave: onDocumentDrag
	});
	

	function load() {
		project.activeLayer.removeChildren();
		loadimg();
	}

	function loadimg() {
		raster = new Raster();
		raster.sendToBack();
		var addr = document.getElementById("imageurl").value;
		raster.source = addr;
		//raster.source = 'http://upload.wikimedia.org/wikipedia/en/2/24/Lenna.png';
		raster.position = view.center;
		console.log(raster.bounds.width);
		console.log(raster.bounds.height);
		raster.scale(0.77);
		//return;
	}	
	
	function toggle_image() {
		raster.visible = !raster.visible;
	}

	$('#load').click (function() { load(); });
	$('#send').click (function() { send(); });
	$('#clear').click (function() { clear(); });
	$('#back').click (function() { back(); });
	$('#back10').click (function() { back10(); });
	$('#toggleimg').click (function() { toggle_image(); });
