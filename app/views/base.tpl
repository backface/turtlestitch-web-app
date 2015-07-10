<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<title>TurtleStitch {{title or '!'}}</title>
	<link rel="shortcut icon" href="/media/img/favicon-32x32.png" type="image/png">	
	<link href="/media/css/bootstrap.min.css" rel="stylesheet" />
	<link href="/media/css/font-awesome.min.css" rel="stylesheet" />
	<link href="/media/css/turtlestitch.css" rel="stylesheet" />
	<script src="/media/js/jquery.min.js"></script>
	<script src="/media/js/bootstrap.min.js"></script>
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
         
		<span class="navbar-brand">
			<a href="/"><img alt="TurtleStitch" src="/media/img/stitchcode_logo_small.png"></a>
		</span>

        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li class="{{get('about_active', '')}}"><a href="/about">About</a></li>
            <li class="{{get('gallery_active', '')}}"><a href="/gallery">Gallery</a></li>
            <li class="{{get('run_active', '')}}"><a href="/run">Run</a></li>
            <li><a href="http://www.stitchcode.com/category/turtlestitch/">Blog</a></li>            
            <!--<li class="{{get('doc_active', '')}}"><a href="/docs">Documentation</a></li>-->
          </ul>
          <ul class="nav navbar-nav navbar-right">			  
			%if userinfo: 
				<li><a style="padding-right:0px;padding-bottom:0px;" href="/profile"><img src="{{userinfo['gravatar_url']}}" /></a></li>
				<li><a href="/logout">Log Out</a></li>
			% else:
				<li><a href="/signup">Sign Up</a></li>	
				<li><a href="/login">Log In</a></li>			
			%end
			<li class="{{get('contact_active', '')}}"><a href="/contact">Contact</a></li>
          </ul>
        </div>
      </div>
    </nav>

	<div class="container">
		{{!base}}
	</div>

</body>
</html>
