% rebase('base.tpl', title=' - User list')

<div class="container">

<h3 class="form-signup-heading">Users</h3> 

% if message: 
 
<div class="container">
  <div class="alert alert-danger alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>Error</h3>
	<div>
		% for line in message:
		{{line}}<br />
		% end
	</div>
  </div>
</div>

% end

 

<div class="row">
	% for item in items:
	<div class="col-sm-1 text-center cell">
	{{item['name']}}<br />
	<a href="/profile/{{item['name']}}"><img class="img-responsive center-block" src="{{item['gravatar']}}" /></a>		
	</div>
	% end
</div>



	
</div>
