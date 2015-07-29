
% rebase('draw/base.tpl', title=' - draw!')
% closed = False

<div class="container">

	<center>
	Optional: URL einer Bildvorlage
	
	<input id="imageurl" type="text" size="40" name="url" />
	<input id="load" type="submit" value="load" />
	<input id="toggleimg" type="submit" value="toggle image visibility" />

	<canvas id="myCanvas"></canvas><br />
	<label for="name">Name</label>
	<input id="name" type="text" size="40" name="name" />
	<input id="send" type="submit" value="save" />
	<input id="clear" type="submit" value="clear" />
	<input id="back" type="submit" value="back" />
	<input id="back10" type="submit" value="back10" />
	
	<div id="result"></div>
        <br>
	</center>
</div>
