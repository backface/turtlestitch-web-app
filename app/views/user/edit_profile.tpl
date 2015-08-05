% rebase('base.tpl', title=' - Edit profile')

<div class="container">

<h3 class="form-signup-heading">Edit profile</h3> 


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


  
	<div class="col-md-5">

<form id="profilmeFor" class="form-horizontal" method="post" action="/edit_profile">	

	<div class="form-group has-feedback">
	  <label for="email" class="control-label col-md-3">E-Mail:</label>
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-envelope"></span>
		</div>
		<input type="email" required class="form-control" name="email" id="email" placeholder="E-Mail" value="{{email}}"/>
		<span class="glyphicion form-control-feedback"></span>
	  </div>
	</div>	 	  
	 
	<div class="form-group has-feedback">	  
	  <label for="link" class="control-label col-md-3">URL/Link</label>
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-link"></span>
		</div>
		<input type="url" class="form-control" name="link" id="link" placeholder="http://www.somedomain.com" value="{{link}}" 
			pattern="(http|https|ftp)\:\/\/[a-zA-Z0-9\-\.\/]*" />
		<span class="glyphicion form-control-feedback"></span>
	  </div>
	</div>	  
	
	<div class="form-group has-feedback">	  
	  <label for="fullname" class="control-label col-md-3">Full name</label>
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-link"></span>
		</div>
		<input type="test" class="form-control" name="fullname" id="fullname"  value="{{fullname}}"/>
		<span class="glyphicion form-control-feedback"></span>
	  </div>
	</div>		
	
	<div class="form-group pull-right">
	  <label for="description" class="control-label">About me:</label>
	  <div class="input-group">
		<textarea cols="40" rows="10" name="description" id="description">{{description}}</textarea>
	  </div>
	</div>	 
		
	<div class='clearfix'></div>
	
	  <div class="form-group ">
		<div class="col-md-3">  
		   <div class="btn-group">    
			<button class="btn btn-lg btn-primary btn-block" type="submit" id="update">Update</button>     
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

  <div class="col-md-1">
		&nbsp;
  </div>

  <div class="col-md-6">
		Profile images via <a href="http://www.gravatar.com">gravatar.com</a>
  </div>

</div>
