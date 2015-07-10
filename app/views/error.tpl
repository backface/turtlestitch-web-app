% rebase('base.tpl', title='')

% if message: 

<div class="container">
  <div class="alert alert-danger alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>{{message_header}}</h3>
	<div>{{message}}</div>
  </div>
</div>

% end
