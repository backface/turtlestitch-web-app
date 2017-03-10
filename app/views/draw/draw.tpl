
% rebase('draw/base.tpl', title=' - draw!')
% closed = False


	<center>
	Optional: URL einer Bildvorlage
	
	<input id="imageurl" type="text" size="40" name="url" />
	<input id="load" type="submit" value="load" />
	<input id="toggleimg" type="submit" value="toggle image visibility" />
	<br />

	<canvas id="myCanvas" style="width:{{canvas_width}}px;height:{{canvas_height}}px"></canvas><br />
	
	<label for="name">Name</label>
	<input id="name" type="text" size="40" name="name" />
	<input id="send" type="submit" value="save" />
	<input id="clear" type="submit" value="clear" />
	<input id="back" type="submit" value="back" />
	<input id="back10" type="submit" value="back10" />
	
	<div id="result"></div>
        <br>
	</center>

