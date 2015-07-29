% rebase('draw/base.tpl', title=' - Gallery View: ' +item["title"])

<div class="container">
	<div class="spacer">&nbsp;</div>
	<div class="spacer">&nbsp;</div>
	<div class="row">
		<div class="col-md-1"></div>
		<div class="col-md-5 text-right">
			<img class="img-responsive pull-right bmargin" src="{{item['media_path']}}/{{item['png_file']}}" />
		</div>
		<div class="col-md-5">

			<form id="profilmeFor" enctype="multipart/form-data" class="form-vertical" method="post" action="/draw/update/{{item["id"]}}">				
			<div class="form-group hase-feedback">
				  <label for="title" class="control-label">Title:</label>
				  <div class="input-group">
					<input type="text" required autofocus class="form-control" name="title" id="title" value="{{item['title']}}"/>
					<span class="glyphicion sform-control-feedback"></span>
				  </div>
				</div>	  				 	  
				 
				<div class="form-group has-feedback">
				  <label for="description" class="control-label">Description:</label>
				  <div class="input-group">
					<textarea cols="40" rows="6" name="description" id="description">{{item['description']}}</textarea>
				  </div>
				</div>	 
				
			
			% if is_admin:
				<div class="spacer"></div>
				<legend>admin functions</legend>
				<div class="form-group has-feedback">
				  <label for="owner_id" class="control-label">Owner ID:</label>
				  <div class="input-group">
					<input type="number" class="form-control" name="owner_id" id="owner_id" min=0 value="{{item['owner_id']}}"/>
				  </div>
				</div>	 	
				<div class="form-group has-feedback">
				  <label for="featured" class="control-label">Featured</label>
				  <div class="input-group">
					<input type="checkbox" class="form-control" name="featured" id="featured" value="1" {{item['featured']}}/>
				  </div>
				</div>	 			
			% end 
			
			  <div class="form-group">
				   <div class="btn-group">    
					<button class="btn btn-lg btn-primary btn-block" type="submit" id="update">Update</button>     
				  </div> 
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
			<div class="spacer"></div>
		
		</div>
		
		
	</div>		

</div>
