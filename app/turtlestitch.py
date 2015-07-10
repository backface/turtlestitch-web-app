#!/usr/bin/python 

import glob, os, time, random, string
import stitchcode
import bottle
import sys
import crypt
import hashlib, urllib

from bottle import Bottle, run, template, install
from bottle import request, response, redirect
from bottle_sqlite import SQLitePlugin
install(SQLitePlugin(dbfile=os.path.dirname(__file__)+'/db/turtlestitch.db'))

app = bottle.default_app()
application = app
salt = "2139080jikasf"

# path settings
upload_abs_path = "%s/../media/uploads" % (os.path.dirname(__file__))
upload_www_path = "/media/uploads"
project_path = "%s/../media/projects" % (os.path.dirname(__file__))
project_www_path = "/media/projects"  
    

###################        
# index
###################      
@app.route('/')
def index(db):
	userinfo = is_logged_in(db)
	return template('index', userinfo=userinfo)
	

###################      
# upload handler
###################    
@app.route('/upload',method='post')
def upload(db):
	xarr = request.POST.getlist("x[]")
	yarr = request.POST.getlist("y[]")
	jarr = request.POST.getlist("j[]")
	
	if len(xarr) == len(yarr) == len(jarr) and len(xarr) > 1:
		pixels_per_millimeter = 10
		emb = stitchcode.Embroidery()

		lx = -99999999
		ly = -99999999
		
		fid = str(int(time.time() * 1000))
			
		for i in range(0, len(xarr)):
			x = float(xarr[i])
			y = float(yarr[i])*-1;
			if jarr[i] == "true":
				j = True
			else:
				j = False
				
			if not(x == lx and y == ly):
				emb.addStitch(stitchcode.Point(x,y,j))
			lx = x
			ly = y
			
		emb.translate_to_origin()	
		emb.flatten()
		emb.scale(27.80/pixels_per_millimeter)
		emb.add_endstitches_to_jumps(10)
		emb.save_as_exp("%s/%s.exp" % (upload_abs_path,fid) )	
		x,y = emb.getSize()
		if x*y < 4000000:
			emb.save_as_png("%s/%s.png" % (upload_abs_path,fid), True)
		else:
			print "image to big: %dx%d = %d" % (x,y,x*y)
			return "ERROR"	
			
		userinfo = is_logged_in(db) 
		print userinfo["id"]
		c = db.execute(
			'insert into designs (id,title,user_id,description) values(?, ?, ?,"")', 
			(fid,fid,userinfo["id"]))
		db.commit()
			
		return fid
	else:
		return "ERROR"
    
###################        
# gallery overview
###################    
@app.route('/gallery')
@app.route('/gallery/page/<page>')
def gallery_list(db,page=1):
	userinfo = is_logged_in(db)
	
	source="db"
	if source == "files":
		# list files
		images = glob.glob("%s/*.png" % upload_abs_path);	

		#pagination stuff
		img_per_page = 20;
		page = int(page)
		if page <= 0:
			page = 1
		num_files = len(images)
		num_pages = len(images) / float(img_per_page)
		if num_pages > int(num_pages):
			num_pages = int(num_pages+1)
		else:
			num_pages = int(num_pages);
		start = (int(page)-1) * img_per_page
		stop = start + img_per_page -1
		
		# now go trough the file list
		items = []
		images.sort(reverse=True);
		i = 0
		for image in images:
			part = image.split("/")
			name = part[-1]
			item = {}
			item["id"] = part[-1][:-4]
			item["image"] = image
			item["file"] = part[-1]
			item["png_file"] = "%s.png" % (item["id"])
			item["exp_file"] = "%s.exp" % (item["id"])
			item["media_path"] = upload_www_path
			if i >= start and i <= stop:
				items.append(item)
			i += 1
	
	if source == "db":
		c = db.execute('''select 
				designs.id, designs.title, designs.description, 
				users.username 
			from designs left outer join users
			on designs.user_id = users.id
			order by designs.timestamp desc''')
		rows = c.fetchall()
		
		#pagination stuff
		img_per_page = 20;
		page = int(page)
		if page <= 0:
			page = 1
		num_files = len(rows)
		num_pages = len(rows) / float(img_per_page)
		if num_pages > int(num_pages):
			num_pages = int(num_pages+1)
		else:
			num_pages = int(num_pages);
		start = (int(page)-1) * img_per_page
		stop = start + img_per_page -1
		
		# now go trough the list
		items = []
		i = 0
		for row in rows:
			item = {}
			item["id"] = row[0]
			item["title"] = row[1]			
			item["description"] = row[2]
			item["owner"] = row[3]
			if userinfo:
				item["is_owner"] = (row[3] == userinfo["username"])
			else:
				item["is_owner"] = False	
			item["png_file"] = "%s.png" % (row[0])
			item["exp_file"] = "%s.exp" % (row[0])
			item["media_path"] = upload_www_path
			if i >= start and i <= stop:
				items.append(item)
			i += 1		
	
	return template('gallery/list',
		items=items, userinfo=userinfo, page=page, pages=num_pages,
		total=num_files, 
		is_admin = is_admin(userinfo),
		gallery_active="active")    

###################        
# gallery detail
###################    
@app.route('/view/<gid>')
def gallery_view(db,gid=0,message=False):
	userinfo = is_logged_in(db)
	
	source="db"
	if source == "files":
		
		item = {}
		item["image"] = "%s/%s.png" % (upload_www_path,gid)
		item["id"] = gid
		item["file"] = "%s.png" % (gid)
		item["exp_file"] = "%s.exp" % (gid)
		item["pes_file"] = "%s.pes" % (gid)
		item["png_file"] = "%s.png" % (gid)
		item["svg_file"] = "%s.svg" % (gid)
		item["url"] =  request.url 
		item["media_path"] = upload_www_path
		
		if not os.path.isfile("%s/%s" % (upload_abs_path, item["exp_file"])):
			return render_error(db,"File does not exist");

		if not os.path.isfile("%s/%s" % (upload_abs_path, item["svg_file"])):
			emb = stitchcode.Embroidery()
			emb.import_melco("%s/%s" % (upload_abs_path, item["exp_file"]))
			emb.scale(1.0)
			emb.save_as_svg("%s/%s" % (upload_abs_path, item["svg_file"]))		

		return template('gallery/view', 
			item=item, userinfo=userinfo,
			message=message,
			gallery_active="active")   
	
	if source == "db":	
		c = db.execute('''select 
						designs.id, designs.title, designs.description, 
						users.username 
					from designs left outer join users
					on designs.user_id = users.id 
					where designs.id = ?''',(gid,))
		row = c.fetchone()
		if not row:
			return render_error(db,"File does not exist");	    

		item = {}
		item["id"] = row[0]
		item["title"] = row[1]			
		item["description"] = row[2]
		item["owner"] = row[3]
		if userinfo:
			item["is_owner"] = (row[3] == userinfo["username"])
		else:
			item["is_owner"] = False			
		item["png_file"] = "%s.png" % (item["id"])
		item["exp_file"] = "%s.exp" % (item["id"])
		item["svg_file"] = "%s.svg" % (item["id"])
		item["pes_file"] = "%s.pes" % (item["id"])
		item["media_path"] = upload_www_path	
		item["url"] =  request.url 
		
		if not os.path.isfile("%s/%s" % (upload_abs_path, item["exp_file"])):
			return render_error(db,"File does not exist");

		if not os.path.isfile("%s/%s" % (upload_abs_path, item["svg_file"])):
			emb = stitchcode.Embroidery()
			emb.import_melco("%s/%s" % (upload_abs_path, item["exp_file"]))
			emb.scale(1.0)
			emb.save_as_svg("%s/%s" % (upload_abs_path, item["svg_file"]))		

		return template('gallery/view', 
			item=item, userinfo=userinfo,
			message=message,
			is_admin = is_admin(userinfo),
			gallery_active="active") 			
		
###################        
# gallery edit
###################    
@app.route('/edit/<gid>')
def gallery_edit(db,gid=0):	
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")
		
	c = db.execute('''select 
					designs.id, designs.title, designs.description, 
					users.username 
				from designs left outer join users
				on designs.user_id = users.id 
				where designs.id = ?''',(gid,))
	row = c.fetchone()

	if not row:
		return render_error(db,"File does not exist");	    

	item = {}
	item["id"] = row[0]
	item["title"] = row[1]			
	item["description"] = row[2]
	item["owner"] = row[3]

	item["is_owner"] = (row[3] == userinfo["username"])
	if not item["is_owner"] and not userinfo["is_admin"]:
		return render_error(db,"NOT ALLOWED");	  
				
	item["png_file"] = "%s.png" % (item["id"])
	item["exp_file"] = "%s.exp" % (item["id"])
	item["svg_file"] = "%s.svg" % (item["id"])
	item["pes_file"] = "%s.pes" % (item["id"])
	item["media_path"] = upload_www_path	
	item["url"] =  request.url 
	
	return template('gallery/edit', 
		item=item, userinfo=userinfo,
		gallery_active="active") 

		
###################        
# gallery update
###################    
@app.route('/update/<gid>', method='POST')
def gallery_update(db,gid=0):
	userinfo = is_logged_in(db)
	submitted_title = request.forms.get('title')
	submitted_description = request.forms.get('description')

	c = db.execute('select user_id from designs where id = ?', (gid,))
	row = c.fetchone()
	
	if not row:
		return render_error(db,"File does not exist");

	if row[0] != userinfo["id"] and not userinfo["is_admin"]:
		return render_error(db,"Not allowed");
		
	c = db.execute('update designs set title = ?, description = ? where id = ?', 
			(submitted_title, submitted_description, gid))
	db.commit()
	message = "Your item was changed."	

	return gallery_view(db,gid,message)

###################        
# gallery delete
###################    
@app.route('/delete/<gid>')
def gallery_delete(db,gid=0):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")

	c = db.execute('''select user_id 
				from designs 
				where id = ?''',(gid,))
	row = c.fetchone()
	if not row:
		return render_error(db,"File does not exist");
	else:
		if row[0] == userinfo["id"] or userinfo["is_admin"]:
			c = db.execute('delete from designs where id=?',(gid,))
			files = images = glob.glob("%s/%s.*" % (upload_abs_path,gid));
			for f in files:
				os.unlink(f)
			redirect("/gallery")
		else:
			return render_error(db,"NOT ALLOWED")



@app.route('/gallery/import')
def gallery_import(db):
	userinfo = is_logged_in(db)

	# list files
	images = glob.glob("%s/*.png" % upload_abs_path);	
	num_files = len(images)
	
	ids = []
	c = db.execute('select id from designs')
	rows = c.fetchall()
	for r in rows:
		ids.append(r[0])
		
	print ids
	# now go trough the file list
	items = []
	images.sort(reverse=True);
	
	for image in images:
		part = image.split("/")
		name = part[-1]
		iid = part[-1][:-4] 
		
		if int(iid) not in ids:
			item = {}		
			item["id"] = part[-1][:-4]
			item["image"] = image
			item["file"] = part[-1]
			item["png_file"] = "%s.png" % (item["id"])
			item["exp_file"] = "%s.exp" % (item["id"])
			item["media_path"] = upload_www_path
			items.append(item)
	num_files = len(items);
	
	return template('gallery/import',
		items=items, userinfo=userinfo,
		total=num_files, 
		is_admin = is_admin(userinfo),
		gallery_active="active")   
		

###################            
# PAGES
###################    
@app.route('/about')
def show_about(db):
	userinfo = is_logged_in(db)
	return template('about', userinfo=userinfo, about_active="active") 
	
@app.route('/docs')
def show_docs(db):
	userinfo = is_logged_in(db)
	return template('docs', userinfo=userinfo, doc_active="active")
   
@app.route('/contact')
def show_index(db):
	userinfo = is_logged_in(db)
	return template('contact', userinfo=userinfo,  contact_active="active")        

	
###################            
# CLOUD
################### 	

@app.route('/cloudlogin', method='POST')
def cloud_login(db):
	submitted_username = request.forms.get('username')
	submitted_password = request.forms.get('password')
	c = db.execute('select id, password from users where username = ?', (submitted_username,))
	row = c.fetchone()
	
	if not row:
		return "INVALID USER"
	cryptedpassword = row[1]
    
	if not crypt.crypt(submitted_password,cryptedpassword) == cryptedpassword:
		return "INVALID PASSWORD"
        
	user_id = row[0]
	time_now = str(int(time.time()))
	new_session_id = time_now + '-' + ''.join([random.choice(string.lowercase) for i in range(6)])
	c = db.execute("insert into sessions (session_id, user_id) values (?,?)",(new_session_id, user_id))
	db.commit()
	response.set_cookie('session_id', new_session_id)
	return "OK"

    
@app.route('/cloudlogout', method='GET')  
def cloud_logout(db):
    session_id = request.get_cookie('session_id')
    db.execute('delete from sessions where session_id = ?', (session_id,))
    response.delete_cookie('session_id')
    return "OK"

    
@app.route('/cloud/signup', method='GET')  
def cloud_signup(db):
	# TODO cloud signup
	pass


@app.route('/cloudloggedin')  
def cloud_logout(db):
    session_id = request.get_cookie('session_id')    
    if not session_id: return "FALSE"
    c = db.execute('select user_id from sessions where session_id = ?', (session_id,))
    row = c.fetchone()
    if row:
        c = db.execute('select username from users where id = ?', (row[0],))
        row = c.fetchone()
        return row[0]
    else:
        return "FALSE" 
   


@app.route('/cloud/get_project', method='GET')  
def project_get(db):
	# TODO cloud get project
	pass

@app.route('/cloud/list_projects', method='GET')  
def projects_list(db):
	# TODO cloud get project list= 
	pass

	
@app.route('/cloud/save_project', method='GET')  
def projects_save(db):
	# TODO cloud save project
	pass
	

###################           
# USER AUTH 
###################  

def is_logged_in(db):
	session_id = request.get_cookie('session_id')    
	if not session_id: return False
	c = db.execute('select user_id from sessions where session_id = ?', (session_id,))
	row = c.fetchone()
	if row:
		c = db.execute('select id, username, email, role from users where id = ?', (row[0],))
		row = c.fetchone()
		if row:
			gravatar_url=get_gravatar_url(row[2])
			r = {
				"id":row[0],
				"username":row[1],
				"email":row[2],
				"is_admin":row[3] == "admin",
				"gravatar_url": gravatar_url
			}
			return r
		else:
			return False
	else:
		return False
        
def get_user_id(db):
    session_id = request.get_cookie('session_id')    
    if not session_id: return False
    c = db.execute('select user_id from sessions where session_id = ?', (session_id,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        return False        
        
def is_admin(userinfo):
    #session_id = request.get_cookie('session_id')    
    #if not session_id: return False
    #c = db.execute('select user_id from sessions where session_id = ?', (session_id,))
    #row = c.fetchone()
    #if row:
	#	c = db.execute('select role from users where id = ?', (row[0],))
	#	row = c.fetchone()
	#	sys.stderr.write(row[0])
	#	if row[0] == "admin":
	#		return True
	#	else:
	#		return False
    #else:
    #    return False        
	if not userinfo:
		return False
	else:
		return userinfo["is_admin"]
    
        
@app.route('/login')
def login(db):
    userinfo = is_logged_in(db)
    print userinfo
    if userinfo:
        redirect("/gallery")
    else:
        return template('user/login', userinfo=userinfo, message="")

@app.route('/login', method='POST')
def do_login(db):
    submitted_username = request.forms.get('username')
    submitted_password = request.forms.get('password')
    
    c = db.execute('select id, password from users where username = ?', (submitted_username,))
    row = c.fetchone()
    cryptedpassword = row[1]
    if not crypt.crypt(submitted_password,cryptedpassword) == cryptedpassword or not row:
        return template('user/login', userinfo=False, message="username or password do not match")
        
    user_id = row[0]
    time_now = str(int(time.time()))
    new_session_id = time_now + '-' + ''.join([random.choice(string.lowercase) for i in range(6)])
    c = db.execute("insert into sessions (session_id, user_id) values (?,?)",(new_session_id, user_id))
    db.commit()
    response.set_cookie('session_id', new_session_id)
    redirect('/')

@app.route('/logout')
def do_logout(db):
    session_id = request.get_cookie('session_id')
    db.execute('delete from sessions where session_id = ?', (session_id,))
    response.delete_cookie('session_id')
    redirect('/login')


###################           
# USER Signup and management
###################  


@app.route('/signup')
def signup(db):
	return template('user/signup',
		userinfo = False,
		username="", message="", email="", link="")	
            
@app.route('/signup',method="POST")
def do_signup(db):
	submitted_username = request.forms.get('username')
	submitted_link = request.forms.get('link')
	submitted_email = request.forms.get('email')
	submitted_password = request.forms.get('password')
	submitted_confirm_password = request.forms.get('confirm_password')	

	message = []
	error = False
	
	if len(submitted_username) < 1:
		error = True
		message.append("Username is required")
		
	if len(submitted_username) < 3 or len(submitted_username) > 15:
		error = True
		message.append("Username has to be between 3 and 15 characters long")

	if len(submitted_email) < 1:
		error = True
		message.append("E-Mail is required")
		
	if len(submitted_password) < 1:
		error = True
		message.append("A Password is required")
		
	if submitted_password != submitted_confirm_password:
		error = True
		message.append("Passwords do not match")
		
	c = db.execute('select id, password from users where username = "%s"' % (submitted_username))
	row = c.fetchone()
	if row:
		error = True
		message.append("Username exists.")		
	else:
		c = db.execute('select id from users where email = "%s"' % (submitted_email))
		row = c.fetchone()
		if row:
			error = True
			message.append("E-Mail already registered")	
				
	if not error:	
		password = crypt.crypt(submitted_password,salt)
		c = db.execute('insert into users (username, email, password, link) values (?, ?, ?, ?)', 
			(submitted_username, submitted_email, password, submitted_link))
		redirect("/login")
		
	else:
		
		return template('user/signup', 
			username=submitted_username, 
			message=message, 
			link=submitted_link,
			email=submitted_email)


@app.route('/profile')
def profile_my(db):
	return profile_show(db,"")
		
@app.route('/profile/<username>')
def profile_show(db,username=""):
	userinfo = is_logged_in(db)
	is_me = False
	if username == "":
		if userinfo:
			username = userinfo["username"]
			is_me = True

	c = db.execute('''select 
			email, link, description, fullname
		from users 
			where username = "%s"''' % (username))
	row  = c.fetchone()
	
	if not row:
		return render_error(db,"unknown user")
	else:
		(email, link, description, fullname) = row
		gravatar_url = get_gravatar_url(email)

		c = db.execute('''select 
				designs.id, designs.title, designs.description, 
				users.username 
			from users, designs
			where users.username=? and designs.user_id = users.id
			order by designs.timestamp desc
			''',(username,))
		rows = c.fetchall()
		
		items = []
		for row in rows:
			item = {}
			item["id"] = row[0]
			item["title"] = row[1]			
			item["description"] = row[2]
			item["owner"] = row[3]
			if userinfo:
				item["is_owner"] = (row[3] == userinfo["username"])
			else:
				item["is_owner"] = False	
			item["png_file"] = "%s.png" % (row[0])
			item["exp_file"] = "%s.exp" % (row[0])
			item["media_path"] = upload_www_path
			items.append(item)
	
		return template('user/profile',
			items=items, 
			userinfo=userinfo, 
			username=username,
			fullname=fullname,
			description=description,
			link=link,
			gravatar_url=gravatar_url,
			is_me=is_me,
			is_admin=is_admin(userinfo),
			message="", header="")	


@app.route('/edit_profile')
def profile_edit(db):
	userinfo = is_logged_in(db)
	
	c = db.execute('''select 
			email, link, fullname, description  
		from users where username = "%s"'''
		 % (userinfo["username"]))
	(email,link,fullname, description) = c.fetchone()	
	
	return template('user/edit_profile',
		userinfo=userinfo, 
		message="", 
		email=email, link=link)	
            
@app.route('/edit_profile',method="POST")
def profile_update(db):
	userinfo = is_logged_in(db)
	submitted_link = request.forms.get('link')
	submitted_email = request.forms.get('email')

	message = []
	error = False
	
	if len(submitted_email) < 1:
		error = True
		message.append("E-Mail is required")
		
	if len(submitted_email) > 50:
		error = True
		message.append("E-Mail too long")
				
	if not error:	
		c = db.execute('update users set email=?, link=? where username =?',
			(submitted_email, submitted_link, userinfo["username"]))
		message = "Your profile was updated";
		gravatar_url = get_gravatar_url(submitted_email)
		return template('user/profile',
			username=userinfo["username"],
			userinfo=userinfo, gravatar_url=gravatar_url,
			message=message, message_header="Success")
		
	else:		
		return template('user/edit_profile', 
			userinfo=userinfo,
			message=message, 
			link=submitted_link,
			email=submitted_email)


@app.route('/change_password')
def password_change(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		redirect("/")
	return template('user/change_password', userinfo=userinfo, message="", email="", link="")	
            
@app.route('/change_password',method="POST")
def password_update(db):
	userinfo = is_logged_in(db)
	
	submitted_old_password = request.forms.get('old_password')
	submitted_password = request.forms.get('password')
	submitted_confirm_password = request.forms.get('confirm_password')	

	message = []
	error = False

	if len(submitted_old_password) < 4:
		error = True
		message.append("Old Password is required (too short)")
			
	if len(submitted_password) < 4:
		error = True
		message.append("Password is too short (min. 4 chars")

	if len(submitted_password) > 15:
		error = True
		message.append("Password is too long (max. 15 chars")
				
	if submitted_password != submitted_confirm_password:
		error = True
		message.append("Passwords do not match")

	c = db.execute('select id, password from users where username = ?', (username,))
	row = c.fetchone()		
	if not row:
		return "INVALID USER"
		
	cryptedpassword = row[1]	
	if not crypt.crypt(submitted_password,cryptedpassword) == cryptedpassword:
		error = True
		message.append("Old password invalid")
				
	if not error:	
		password = crypt.crypt(submitted_password,salt)
		c = db.execute('update users set password = ? where username = ?', 
			(password, username))
		message = "Your password was changed."
		return template('message', 
			userinfo=userinfo, 
			message=message,  
			message_header="Success")
	else:		
		return template('user/change_password', 
			userinfo=userinfo, 
			essage=message,  
			message_header="Error")



###################################################
# helper function 
####################################################

def render_error(db,string):
	userinfo = is_logged_in(db)	
	return template('error', 
		userinfo=userinfo, 
		message=string,  
		message_header="Error")
		
def render_message(db,string,header=""):
	userinfo = is_logged_in(dnb)	
	return template('message', 
		userinfo=userinfo, 
		message=string,  
		message_header=header)		


def get_gravatar_url(email):
	#default = "http://www.example.com/default.jpg"
	size = 24	
	gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
	#gravatar_url += urllib.urlencode({'d':default, 's':str(size)})	
	gravatar_url += urllib.urlencode({'s':str(size)})	
	return gravatar_url

###################################################
# deployment 
####################################################

# if run from shell (
#if __name__ == "__main__":
#	debug(True)
#	run(app, host='localhost', port=8080)

# if run via cgi
#bottle.debug(True)
#bottle.run(server='cgi')

# another way to run via cgi
#if __name__ == '__main__':
#   from wsgiref.handlers import CGIHandler
#   CGIHandler().run(bottle.default_app())