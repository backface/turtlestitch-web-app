% rebase('base.tpl', title=' - Edit Page')

<div class="container">

<h3 class="form-signup-heading">Edit Page</h3> 


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

% if new_page:
<form id="profilmeFor" class="form-vertical" method="post" action="/page/create">
% else:
<form id="profilmeFor" class="form-vertical" method="post" action="/page/update/{{slug}}">
% end

	<div class="col-md-6">

		<div class="form-group has-feedback">
		  <label for="title" class="control-label">Title</label>
		  <div class="input-group">
			<input type="title" required class="form-control" name="title" id="title" value="{{title}}"/>
		  </div>
		</div>	 	  
		 
		<div class="form-group has-feedback">
		  <label for="slug" class="control-label">Slug</label>
		  <div class="input-group">
			<input type="slug" class="form-control" name="slug" id="slug" value="{{slug}}"/>
		  </div>
		</div>	  

		<div class="form-group">
		  <label for="content" class="control-label">Content</label>
		  <div class="input-group">
			<textarea cols="80" rows="15" name="content" id="content">{{content}}</textarea>
		  </div>
		</div>	 
			
		% if not new_page:
			<div class="form-group ">
				<div class="col-md-3">  
				   <div class="btn-group">    
					<button class="btn btn-lg btn-primary btn-block" type="submit" id="update">Update</button>     
				  </div> 
				</div>
			</div>
		% else:
			<div class="form-group ">
				<div class="col-md-3">  
				   <div class="btn-group">    
					<button class="btn btn-lg btn-primary btn-block" type="submit" id="create">Create</button>     
				  </div> 
				</div>
			</div>
		
		% end

  
  </div>
    
 
</form>

<script>
	$(document).ready(function() {
		$("input").keyup(function () {
			var formGroup = $(this).parents(".form-group");
			
			if (this.checkValidity()) {
				formGroup.addClass("has-success").removeClass("has-error");
			} else {
				formGroup.addClass("has-error").removeClass("has-success");
			}
	});
});		
</script>

</div>
