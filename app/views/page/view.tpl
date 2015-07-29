% rebase('base.tpl', title='- ' + pagetitle)



% if is_admin:
<div class="container">
	<a href="/page/edit/{{slug}}"><span class="glyphicon glyphicon-edit"></span>edit</a><br />	
</div>
% end


% if message: 

<div class="container">
  <div class="alert alert-success alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
	<h3>{{message_header}}</h3>
	<div>{{message}}</div>
  </div>
</div>

% end


{{!content}}



