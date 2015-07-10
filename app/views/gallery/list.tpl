% rebase('base.tpl', title=' - Gallery')
% closed = False
<div class="container">


	
	<div class="row">&nbsp;
	%if pages > 1:	
    <ul class="pagination  pull-right">
		<li><a href="/gallery">&laquo;</a></li>
    % for cp in range(0,pages):
        %if page == cp+1:
			<li class="active"><span>{{cp+1}}</span></li>
		% else:
        <li><a href="/gallery/page/{{cp+1}}">{{cp+1}}</a></li>
		% end
    % end
		<li><a href="/gallery/page/{{pages}}">&raquo;</a></li>
    </ul>
	% end    
	</div>
	

	% i = 0
	% for item in items:
		% if i % 4 == 0:
		% closed = False
		<div class="row">
		% end
		<div class="col-sm-3 text-center cell">
			<h5>{{item['title']}}</h5><br />
			<a href="/view/{{item['id']}}"><img class="img-responsive center-block" src="/media/uploads/{{item['png_file']}}" /></a>
			
			% if is_admin or item['is_owner']:
			<a href="/edit/{{item['id']}}"><span class="glyphicon glyphicon-edit"></span> edit</a><br />
			<a href="/delete/{{item['id']}}"><span class="glyphicon glyphicon-remove"></span> delete</a>		
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
