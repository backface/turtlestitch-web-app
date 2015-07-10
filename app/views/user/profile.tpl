% rebase('base.tpl', title=username+"'s profile", userinfo=userinfo)

% if message: 

<div class="container">
  <div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>{{message_header}}</h3>
	<div>{{message}}</div>
  </div>
</div>

% end

<div class="container">
	<div class="row">
		<div class="col-md-4"><h3><img class="pull-right bargmin" src="{{gravatar_url}}" /></h3></div>
		<div class="col-md-4">
			<h3>{{username}} 
			% if fullname: 
				{{fullname}}
			% end
		</div>
	</div>
	
	% if is_me:
		<div class="row">
			<div class="col-md-4"></div>
			<div class="col-md-4">
				<p>
				<a href="/edit_profile"><span class="glyphicon glyphicon-edit"></span> Edit Profile</a><br />
				<a href="/change_password"><span class="glyphicon glyphicon-edit"></span> Change Password</a>
				</p>
			</div>	
		</div>
	% end

	<div class="row">
		<div class="col-md-4"></div>
		<div class="col-md-4">
			% if link: 
				<p><a href="{{link}}">{{link}}</a></p>
			% end
			
			% if description: 
				<p>{{link}}</p>
			% end
		</div>
	</div>	
</div>


% closed = False
<div class="container">

	% i = 0
	% for item in items:
		% if i % 4 == 0:
		% closed = False
		<div class="row">
		% end
		<div class="col-sm-3 text-center cell">
			<h5>{{item['title']}}</h5><br />
			<a href="/view/{{item['id']}}"><img class="img-responsive center-block" src="/media/uploads/{{item['png_file']}}" /></a>
			
			% if is_admin or item['is_owner']:
			<a href="/edit/{{item['id']}}"><span class="glyphicon glyphicon-edit"></span> edit</a><br />
			<a href="/delete/{{item['id']}}"><span class="glyphicon glyphicon-remove"></span> delete</a>		
			% end
		
		</div>
		% i += 1
		% if i % 4 == 0:
		</div>
		% closed = True
		% end		
	% end
	%if not closed:
	</div>
	% closed = True
	% end	

</div>

