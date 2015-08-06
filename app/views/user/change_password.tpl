% rebase('base.tpl', title=' - Change Password')

<div class="container">

<h3 class="form-signup-heading">Change Password</h3> 

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

<form id="passwordForm" class="form-horizontal" method="post" action="/change_password">
  
	<div class="col-md-7">

	<div class="form-group has-feedback">  
	  <label for="old_password" class="control-label col-md-3">Old Password:</label>
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-lock"></span>
		</div>
		<input type="password" required class="form-control" name="old_password" id="old_password" placeholder="Old Password" pattern="\w{5,20}" />
		<span class="glyphicion form-control-feedback"></span>
	  </div>
	</div> 
		 	  
	<div class="form-group has-feedback">  
	  <label for="password" class="control-label col-md-3">New Password:</label>
	  <div class="input-group">
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-lock"></span>
		</div>
		<input type="password" required class="form-control" name="password" id="password" placeholder="New Password" pattern="\w{5,20}" />
		<span class="glyphicion form-control-feedback"></span>
	  </div>
	</div> 
	
	<div class="form-group has-feedback">	  
	  <label for="confirm_password" class="control-label col-md-3">Confirm Password:</label>
	  <div class="input-group"> 
		<div class="input-group-addon">
		  <span class="glyphicon glyphicon-lock"></span>
		</div>
		<input type="password" required class="form-control" name="confirm_password" id="confirm_password" placeholder="Confirm Password"  pattern="\w{5,20}" />
		<span class="glyphicion form-control-feedback"></span>
	  </div>	  
	</div> 
	
  <div class=form-group">
	<div class="col-md-3">  
	   <div class="btn-group">    
		<button class="btn btn-lg btn-primary btn-block" type="submit" id="update">Update</button>     
	  </div> 
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
			
			if ($(this).attr('id')=="confirm_password") {
				if ($(this).val() ==  $("#password").val()) {
					formGroup.addClass("has-success").removeClass("has-error");
					glyphicon.addClass("glyphicon-ok").removeClass("glyphicon-remove");
				} else {
					formGroup.addClass("has-error").removeClass("has-success");
					glyphicon.addClass("glyphicon-remove").removeClass("glyphicon-ok");
				}
			}
	});
});		
</script>
