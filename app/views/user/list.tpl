% rebase('base.tpl', title=' - User list')

<div class="container">

<h3 class="form-signup-heading">Users</h3> 

% if message: 
 
<div class="container">
  <div class="alert alert-success alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>{{message["title"]}}</h3>
	<div>
		{{message["text"]}}
	</div>
  </div>
</div>

% end

 

<div class="row">
	% for item in items:
	<div class="col-md-1 text-center cell">
	{{item['name']}}<br />
	<a href="/profile/{{item['name']}}"><img class="img-responsive center-block" src="{{item['gravatar']}}" /></a><br />
	
			% if is_admin:
			<a href="/profile/edit/{{item['id']}}"><span class="glyphicon glyphicon-edit"></span> edit</a><br />
			<a href="/profile/delete/{{item['id']}}"><span class="glyphicon glyphicon-remove"></span> delete</a>		
			% end	
	</div>
	% end
</div>



	
</div>
