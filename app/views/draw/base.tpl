
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<title>Zeichnen & Sticken - drawtool {{title or '!'}}</title>
	
	<link rel="shortcut icon" href="/media/img/favicon-32x32.png" type="image/png">	
	<meta name="description" content="draw tool " />
	
	<link href="/media/css/bootstrap.min.css" rel="stylesheet" />
	<link href="/media/css/font-awesome.min.css" rel="stylesheet" />
	<link href="/media/css/turtlestitch.css" rel="stylesheet" />

	
	<script type="text/javascript" src="/media/js/paper.js"></script>
	<script type="text/javascript" src="/media/js/jquery.min.js"></script>
	<script type="text/javascript" src="/media/js/jquery.fileDownload.js"></script>
	<script type="text/javascript" src="/media/js/baseurl.js"></script>
	<script src="/media/js/bootstrap.min.js"></script>	
	<script type="text/paperscript" canvas="myCanvas"  src="/media/js/stitchtimg.js"></script>

	<link href='http://fonts.googleapis.com/css?family=Economica:400,700' rel='stylesheet' type='text/css'>
	<style>
		h1 {font-family: 'Economica', sans-serif;}
		#result {font-size:10px;font-family:monospaced}
		h1{text-transform:uppercase}
	</style>
	<title>stitchcode webtool</title>
</head>


<body> 
    <nav class="navbar navbar-default navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li class="{{get('draw_active', '')}}"><a href="/draw">Draw</a></li>
            <li class="{{get('gallery_active', '')}}"><a href="/draw/gallery">Gallery</a></li>
          </ul>
          <ul class="nav navbar-nav navbar-right">			  
			%if userinfo: 
				<li><a style="padding-right:0px;padding-bottom:0px;" href="/profile"><img src="{{userinfo['gravatar_url']}}" height="24" width="24" /></a></li>
				<li><a href="/logout">Log Out</a></li>
			% else:
				<!--<li><a href="/signup">Sign Up</a></li>	
				<li><a href="/login">Log In</a></li>	-->		
			%end
          </ul>
        </div>
      </div>
    </nav>

	{{!base}}
</body>
</html>
