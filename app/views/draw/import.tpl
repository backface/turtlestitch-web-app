% rebase('base.tpl', title=' - Gallery import')
% closed = False
<div class="container">

	% i = 0
	% for item in items:
		% if i % 4 == 0:
		% closed = False
		<div class="row">
		% end
		<div class="col-sm-3 text-center cell">
			<h5>{{item['id']}}</h5><br />
			<a href="/view/{{item['id']}}"><img class="img-responsive center-block" src="/media/uploads/{{item['png_file']}}" /></a>
			
			% if is_admin:
			<a href="/import/{{item['id']}}"><span class="glyphicon glyphicon-edit"></span>import</a><br />	
			<a href="/deletefiles/{{item['id']}}"><span class="glyphicon glyphicon-remove"></span>delete</a><br />	
			% end
		
		</div>
		% i += 1
		% if i % 4 == 0:
		</div>
		% closed = True
		% end		
	% end
	%if not closed:
	</div>
	% closed = True
	% end	

</div>
