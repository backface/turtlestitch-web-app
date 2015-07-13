% rebase('base.tpl', title=' - Gallery View: ' +item["title"])

% if message: 

<div class="container">
  <div class="alert alert-success alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>Success</h3>
	<div>{{message}}</div>
  </div>
</div>

% end

<div class="container">
	<div class="spacer">&nbsp;</div>
	<div class="spacer">&nbsp;</div>
	<div class="row">
		<div class="col-md-1"></div>
		<div class="col-md-5 text-right">
			<img class="img-responsive pull-right bmargin" src="{{item['media_path']}}/{{item['png_file']}}" />
			
		</div>
		<div class="col-md-4">
			<h2>{{item['title']}}</h2>
			<p>by <a href="/profile/{{item['owner']}}">{{item['owner']}}</a></p>
			
			% if item['description'] != "None":
			<p>
			% for l in item['description'].split("\n"):
				{{l}}<br />
			% end
			</p>
						
			


			% if item['snap_file']:
			<p class="dlink">
				<span class="glyphicon glyphicon-edit" aria-hidden="true"></span> 
				<a href="/run/index.html#open:..{{item['media_path']}}/{{item['snap_file']}}">Open in TurtleStitch</a><br />
			</p>	
			% end		

			
			<h4>Download as image file</h4>
			<p class="dlink">
				<span class="glyphicon glyphicon-picture" aria-hidden="true"></span> 
				<a href="{{item['media_path']}}/{{item['png_file']}}">{{item['png_file']}}</a><br />
				<span class="glyphicon glyphicon-download" aria-hidden="true"></span> 
				<a href="{{item['media_path']}}/{{item['svg_file']}}">{{item['svg_file']}}</a><br />
			</p>
		
			
			<h4>Download as embroidery file</h4>
			<p class="dlink">
			<span class="glyphicon glyphicon-download" aria-hidden="true"></span> 
				<a href="{{item['media_path']}}/{{item['exp_file']}}">{{item['exp_file']}}</a><br />
				
			</p>
			
			% if item['snap_file']:
			<h4>Download as snap project file</h4>
			<p class="dlink">
				<span class="glyphicon glyphicon-download" aria-hidden="true"></span> 
				<a href="{{item['media_path']}}/{{item['snap_file']}}">{{item['snap_file']}}</a><br />
				
			</p>	
			% end	
			
			<div class="spacer">&nbsp;</div>
			
			<button class="btn btn-default dropdown-toggle" type="button" id="sharebutton" data-toggle="dropdown">
				<span class="glyphicon glyphicon-share" aria-hidden="true"></span> Share
			</button>
			<ul class="dropdown-menu" role="menu" aria-labelledby="sharebutton">
				<li role="presentation">								 
				  <a role="menuitem" tabindex="-1" href="https://twitter.com/share">
					<i class="fa fa-twitter fa-fw"></i>
					Share on Twitter
				  </a>
				</li>
				<li role="presentation">				
				  <a role="menuitem" tabindex="-1" href="http://www.facebook.com/sharer.php">			
					<i class="fa fa-facebook-official fa-fw"></i> Share on Facebook
				  </a>
				</li>				
				<li role="presentation">				  
				<a role="menuitem" tabindex="-1" href="mailto:?subject=Turtlestitch {{item['id']}}&amp;body=Check out: {{item['url']}}">
					<i class="fa fa-envelope-o fa-fw"></i> Share by Email
				  </a>
				</li>												
			</ul>
			
			<div class="spacer">&nbsp;</div>
 
			<p>
			% if is_admin or item['is_owner']:
			<a href="/edit/{{item['id']}}"><span class="glyphicon glyphicon-edit"></span> edit</a><br />
			<a href="/delete/{{item['id']}}"><span class="glyphicon glyphicon-remove"></span> delete</a>		
			% end
			</p>
			

		</div>
		
		<div class="col-md-1"></div>
	</div>

</div>
