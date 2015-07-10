% rebase('base.tpl', title=' - Login')

<h3 class="form-signin-heading">Sign in</h3>

% if message: 

<div class="container">
  <div class="alert alert-danger alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>Error</h3>
	<div>{{message}}</div>
  </div>
</div>

% end


<form class="form-horizontal" method="post" action="/login">
  <div class="form-group">
	<div class="col-md-3">
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-user"></span>
		</div>
		<input type="text" class="form-control" name="username" id="username" placeholder="Username" autofocus />
	  </div>

	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-lock"></span>
		</div>
		<input type="password" class="form-control" name="password" id="password" placeholder="Password" autofocus />
	  </div>
	</div> 
  </div>
  
  <div class="form-group">
	<div class="col-md-3">  
	   <div class="btn-group">    
		<button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>     
	  </div> 
	</div>
  </div>
 
</form>



