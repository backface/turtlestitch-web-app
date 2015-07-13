% rebase('base.tpl', title=' - Login')



<div class="container">
<h3 class="form-signin-heading">Sign in</h3>
</div>

% if message: 

<div class="container">
  <div class="alert alert-danger alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>Error</h3>
	<div>{{message}}</div>
  </div>
</div>

% end

<div class="container">
<form class="form-horizontal" method="post" action="/login">
  <div class="form-group">
	<div class="col-md-3">
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-user"></span>
		</div>
		<input type="text" required class="form-control" name="username" id="username" placeholder="Username" autofocus />
	  </div>

	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-lock"></span>
		</div>
		<input type="password" required class="form-control" name="password" id="password" placeholder="Password" />
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
</div>



<script>
	$(document).ready(function() {
		$("input").keyup(function () {
			var formGroup = $(this).parents(".form-group");
			var glyphicon = formGroup.find(".glyphicon");
			
			if (this.checkValidity()) {
				formGroup.addClass("has-success").removeClass("has-error");
				glyphicon.addClass("glyphicon-ok").removeClass("glyphicon-remove");
			} else {
				formGroup.addClass("has-error").removeClass("has-success");
				glyphicon.addClass("glyphicon-remove").removeClass("glyphicon-ok");
			}
			
	});
});		
</script>




