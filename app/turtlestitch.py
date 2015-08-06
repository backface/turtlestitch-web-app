#!/usr/bin/python
# -*- coding: utf-8 -*-

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
@app.route('/page')
def index(db):
	userinfo = is_logged_in(db)
	return page_view(db,"index")
	#return template('index', userinfo=userinfo)
	

###################      
# upload handler
###################    
@app.route('/upload',method='post')
def upload(db):
	xarr = request.POST.getlist("x[]")
	yarr = request.POST.getlist("y[]")
	jarr = request.POST.getlist("j[]")
	data = request.POST.get('project_data')
	name = request.POST.get('name').decode("utf-8")
	
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
		emb.scale(27.80/pixels_per_millimeter)
		emb.flatten()
		emb.add_endstitches_to_jumps(10)
		emb.save_as_exp("%s/%s.exp" % (upload_abs_path,fid) )	
		x,y = emb.getSize()
		if x*y < 4000000:
			emb.save_as_png("%s/%s.png" % (upload_abs_path,fid), True)
		else:
			print "image to big: %dx%d = %d" % (x,y,x*y)
			return "ERROR"	
			
		userinfo = is_logged_in(db) 
		if not userinfo:
			userid=0
		else:
			userid=userinfo["id"]
			
		if name:
			title = name
		else:
			title = fid
			
		if data:
			f = open("%s/%s.xml" % (upload_abs_path,fid),"w")
			f.write(data);
			f.close() 
			
		c = db.execute(
			'insert into designs (id, title, user_id, description) values(?, ?, ?,"")', 
			(fid, title, userid))
		db.commit()
			
		return "OK:%s" % (fid)
	else:
		return "ERROR"
    
###################        
# gallery overview
###################   


@app.route('/gallery')
@app.route('/gallery/featured')
@app.route('/gallery/featured/page/<page>') 
def gallery_featured(db,page=1):
	return gallery_list(db,page,featured=True)
	
@app.route('/gallery/all')
def gallery_all(db):
	return gallery_list(db,page=1,featured=False)	
	
@app.route('/gallery/textile')
@app.route('/gallery/textile/page/<page>')
def gallery_textile(db,page=1):
	return gallery_list(db,page,featured=False,textile=True)		

@app.route('/gallery/page/<page>')
def gallery_list(db,page=1,featured=False,textile=False):
	userinfo = is_logged_in(db)

	page_link = "/gallery"
	query = '''select 
			designs.id, designs.title, designs.description, 
			users.username 
		from designs left outer join users
		on designs.user_id = users.id
		order by designs.timestamp desc'''
	if featured:
		page_link = "/gallery/featured"
		query = '''select 
			designs.id, designs.title, designs.description, 
			users.username 
		from designs 
		left outer join users
		on designs.user_id = users.id where designs.featured = 1 
		order by designs.timestamp desc'''
	if textile:
		page_link = "/gallery/textile"
		query = '''select 
				designs.id, designs.title, designs.description, users.username,
				designs_images.name 
			from designs 
			left join users on designs.user_id=users.id 
			left join designs_images on designs_images.design_id=designs.id 
			where  designs_images.name != ""
			order by designs.timestamp desc'''
	c = db.execute(query)
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
		
		if textile:
			item["png_file"] = "%s/%s/%s" % ("images",row[0],row[4])
			
		item["exp_file"] = "%s.exp" % (row[0])
		item["media_path"] = upload_www_path
		if i >= start and i <= stop:
			items.append(item)
		i += 1		
	
	return template('gallery/list',
		items=items, userinfo=userinfo, page=page, pages=num_pages,
		total=num_files, 
		featured=featured,
		page_link=page_link,
		textile=textile,
		is_admin = is_admin(userinfo),
		gallery_active="active")    



###################        
# gallery detail
###################    
@app.route('/view/<gid>')
def gallery_view(db,gid=0,message=False):
	userinfo = is_logged_in(db)
	

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
	item["dst_file"] = "%s.dst" % (item["id"])
	item["pes_file"] = "%s.pes" % (item["id"])
	item["snap_file"] = "%s.xml" % (item["id"])
	item["media_path"] = upload_www_path	
	item["url"] =  request.url 
	
	if not os.path.isfile("%s/%s" % (upload_abs_path, item["snap_file"])):
		item["snap_file"] = False
		
	if not os.path.isfile("%s/%s" % (upload_abs_path, item["exp_file"])):
		return render_error(db,"File does not exist");

	# if not exists generate SVG File
	if not os.path.isfile("%s/%s" % (upload_abs_path, item["svg_file"])):
		emb = stitchcode.Embroidery()
		emb.import_melco("%s/%s" % (upload_abs_path, item["exp_file"]))
		emb.scale(1.0)
		emb.save_as_svg("%s/%s" % (upload_abs_path, item["svg_file"]))		

	# if not exists generate DST File
	if not os.path.isfile("%s/%s" % (upload_abs_path, item["dst_file"])):
		emb = stitchcode.Embroidery()
		emb.import_melco("%s/%s" % (upload_abs_path, item["exp_file"]))
		emb.scale(1.0)
		emb.save_as_dst("%s/%s" % (upload_abs_path, item["dst_file"]))
		
	c = db.execute('''select id, name from designs_images whe
						where design_id = ?''',(gid,))
	row = c.fetchall()
	if row:
		item["images"] = []
		for r in row:
			img = {}
			img["id"]= r[0]
			img["name"]= r[1]
			img["src"] = "%s/images/%s/%s" % (upload_www_path, gid, r[1]) 
			item["images"].append(img)
	
	else:
		item["images"] = False
		
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
					users.username, users.id, designs.featured
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
	item["owner_id"] = row[4]
	if row[5]>0:
		item["featured"] = "checked"
	else:
		item["featured"] = ""
		
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
		is_admin=is_admin(userinfo),
		gallery_active="active") 

		
###################        
# gallery update
###################    
@app.route('/update/<gid>', method='POST')
def gallery_update(db,gid=0):
	userinfo = is_logged_in(db)
	submitted_title = request.forms.get('title').decode("utf-8")
	submitted_description = strip_tags(request.forms.get('description')).decode("utf-8")
	submitted_owner_id = request.forms.get('owner_id')
	submitted_featured = request.forms.get('featured')
	if submitted_featured == None:
		submitted_featured = 0

	c = db.execute('select user_id from designs where id = ?', (gid,))
	row = c.fetchone()
	
	if not row:
		return render_error(db,"File does not exist");

	if row[0] != userinfo["id"] and not is_admin(userinfo):
		return render_error(db,"Not allowed");
	
	if is_admin(userinfo):
		c = db.execute('update designs set title = ?, description = ?, user_id = ?, featured = ? where id = ?', 
				(submitted_title, submitted_description, submitted_owner_id, submitted_featured, gid ))
		
	else:
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


###################        
# gallery image delete
###################    
@app.route('/deleteimg/<gid>')
def gallery_deleteimg(db,gid=0):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")

	c = db.execute('''select designs_images.design_id, designs_images.name, designs.user_id
				from designs_images left join designs on designs_images.design_id  = designs.id
				where designs_images.id = ?''',(gid,))
	row = c.fetchone()
	if not row:
		return render_error(db,"File does not exist");
	else:
		if row[0] == userinfo["id"] or userinfo["is_admin"]:
			
			c = db.execute('delete from designs_images where id=?',(gid,))
			db.commit()
			f = "%s/images/%s/%s" % (upload_abs_path, row[0], row[1]);
			print f
			os.unlink(f)
			redirect("/view/%s" % (row[0]))
		else:
			return render_error(db,"NOT ALLOWED")



###################        
# gallery import stuff
###################    

@app.route('/img_upload', method='POST')
def gallery_img_upload(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")	
		
	if 	request.files.get('image_file') == None:
		return render_error(db,"no file specified")	
		
	gid  = request.forms.get('gid')
	upload  = request.files.get('image_file')
	name, ext = os.path.splitext(upload.filename)
	uploaddir = "%s/%s/%s" % (upload_abs_path, "images",gid)
    	
	if ext not in ('.png','.jpg','.jpeg'):
		return 'File extension not allowed.'

	c = db.execute('select * from designs_images where design_id=? and name=?', (gid,upload.filename,))
	row = c.fetchone()
	if row:
		c = db.execute('update designs_images set name=? where design_id=? and name=?', 
			(upload.filename, gid,upload.filename,))
		db.commit()	
	else:
		c = db.execute('insert into designs_images (design_id, name) values (?, ?)', 
			(gid,upload.filename,))
		db.commit()	

	if not os.path.exists(uploaddir):
		os.makedirs(uploaddir)	
			
	upload.save(uploaddir,True) # appends upload.filename automatically
	
	message = "Your item was changed."	

	return gallery_view(db,gid,message)




###################        
# gallery import stuff
###################    

@app.route('/gallery/import')
def gallery_import(db):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		render_error("not allowed");

	# list files
	images = glob.glob("%s/*.png" % upload_abs_path);	
	num_files = len(images)
	
	ids = []
	c = db.execute('select id from designs')
	rows = c.fetchall()
	for r in rows:
		ids.append(r[0])
		
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
		

@app.route('/import/<gid>')
def gallery_do_import(db,gid):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		render_error("not allowed");
			
	c = db.execute(
		'insert into designs (id, title, user_id, description) values(?, ?, ?,"")', 
		(gid, gid, userinfo["id"],))
	db.commit()	

	redirect("/edit/"+gid) 
	
@app.route('/deletefiles/<gid>')
def gallery_deletefiles(db,gid=0):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
	
	files = glob.glob("%s/%s.*" % (upload_abs_path,gid));
	for f in files:
		os.unlink(f)
	
	redirect("/gallery/import")
	
			
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
def cloud_isloggedin(db):
    session_id = request.get_cookie('session_id')    
    if not session_id: return "FALSE"
    c = db.execute('select user_id from sessions where session_id = ?', (session_id,))
    row = c.fetchone()
    if row:
        c = db.execute('select username from users where id = ?', (row[0],))
        row = c.fetchone()
        return "OK:"+row[0]
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
    if not row:
		return template('user/login', userinfo=False, message="username or password do not match")
		
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
    
@app.route('/forgot_password')
def profile_password_reminder(db):
	userinfo = is_logged_in(db)
	return template('user/password_reminder', 
			userinfo=userinfo, 
			email="",
			message="")   

@app.route('/forgot_password',method="POST")
def profile_password_do_reminder(db):
	userinfo = is_logged_in(db)
	submitted_email = request.forms.get('email')
	message = ""
	c = db.execute('select id, password from users where email = ?', (submitted_email,))	
	row = c.fetchone()
   
	if not row:
		message = "Unknown email."	
		return template('user/password_reminder', 
			userinfo=userinfo, 
			email="",
			message=message)
	else:
		reset_id = str(int(time.time() * 1000))
		c = db.execute('update users set reset=? where email = ? ', (reset_id, submitted_email,))	
		send_mail(submitted_email,"do-no-reply@turtlestitch.org",
			"Turtlestitch Password Reset Link",
			"You requested a reset of your password. Follow this link to create your new password:\n"+
				"http://www.turtlestitch.org/reset_password/%s\n\n" % (reset_id))
		
		return template('user/password_reminder_sent', 
				userinfo=userinfo) 


@app.route('/reset_password/<rid>')
def profile_password_reset(db,rid):
	userinfo = is_logged_in(db)
	
	c = db.execute('select id from users where reset = ?', (rid,))	
	row = c.fetchone()
    
	if not row:
		return render_error(db, "Invalid reset link")
	else: 	
		return template('user/reset_password', 
			userinfo=userinfo, 
			rid=rid,
			message="",)	
            
@app.route('/reset_password/<rid>',method="POST")
def profile_password_reset_update(db,rid):
	userinfo = is_logged_in(db)
	submitted_password = request.forms.get('password')
	submitted_confirm_password = request.forms.get('confirm_password')	

	message = []
	error = False

	if len(submitted_password) < 4:
		error = True
		message.append("Password is too short (min. 4 chars")

	if len(submitted_password) > 15:
		error = True
		message.append("Password is too long (max. 15 chars")
				
	if submitted_password != submitted_confirm_password:
		error = True
		message.append("Passwords do not match")
				
	if not error:	
		password = crypt.crypt(submitted_password,salt)
		c = db.execute('update users set password = ?, reset = ? where reset = ?', (password, "", rid,))
		message = "Your password was changed. You can now login again."
		return render_success(db, message)
	else:		
		return template('user/reset_password', 
			userinfo=userinfo, 
			essage=message,  
			message_header="Error")


###################           
# PAGES
###################  

@app.route('/page/create')
def page_new(db):
	userinfo = is_logged_in(db) 
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
	else:
		return template('page/edit',
			userinfo = userinfo,
			new_page=True,
			title="",
			slug="",
			content="",
			username="", 
			message="")
			
@app.route('/page/create',method="POST")
def page_create(db):
	return page_update(db,"",True)

@app.route('/page/edit/<slug>')
def page_edit(db,slug=""):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
			
	c = db.execute('select title, content, slug from pages where slug = ?', (slug,))
	row = c.fetchone()
	
	if row:
		return template('page/edit',
		userinfo =userinfo,
		title=row[0],
		content=row[1],
		slug=row[2],
		new_page=False,
		message="")		
	else:
		return render_error(db,"Page not found")   
		
@app.route('/page/update/<old_slug>',method="POST")
def page_update(db,old_slug,new_page=False,):
	userinfo = is_logged_in(db) 
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
	else:
		
		import re
		submitted_title = request.forms.get('title').decode("utf-8")
		submitted_content = request.forms.get('content').decode("utf-8")
		submitted_slug = request.forms.get('slug').decode("utf-8")
		
		message = []
		error = False	

	
		if len(submitted_title) < 1 or submitted_title==None:
			error = True
			message.append("Title is required")			
	
		if not error:
			if submitted_slug == "" or submitted_slug== None:
				slug = re.sub(r"[^a-zA-Z0-9\n\.]", "_", submitted_title)
			else:		
				slug = re.sub(r"[^a-zA-Z0-9\n\.]", "_", submitted_slug)	
		 
			if not new_page:			
				c = db.execute('update pages set title=?, slug=?, content=? where slug=?', 
					(submitted_title, slug, submitted_content, old_slug))
			else:				
				c = db.execute('insert into pages (title,slug, content) values (?, ?, ?)', 
					(submitted_title, slug, submitted_content))	

			return template('page/view',
				userinfo = userinfo,
				new_page=new_page,
				pagetitle=submitted_title,
				content=submitted_content,
				is_admin = True,
				slug=slug,
				message="page updated.",
				message_header="Success")		
		else:
			return template('page/view',
				userinfo = userinfo,
				new_page=new_page,
				pagetitle="error",
				slug=slug,
				content=submitted_content,
				username="", 
				message=message)		

@app.route('/page/<slug>')
def page_view(db,slug=""):
	userinfo = is_logged_in(db)
	c = db.execute('select title, content from pages where slug = ?', (slug,))
	row = c.fetchone()
	
	if row:		
		return template('page/view',
		userinfo=userinfo,
		pagetitle=row[0],
		content=row[1],
		is_admin = is_admin(userinfo),
		slug = slug,
		message="")		
	else:
		return render_error(db,"Page not found")   


###################           
# USER Signup and management
###################  

@app.route('/users')
def profiles_list(db, message = ""):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	
	c = db.execute('''select 
			username, email, link, fullname, description, id
		from users order by timestamp''')
		 
	rows = c.fetchall();
	
	items = []
	for row in rows:
		item = {}
		item["name"] = row[0]
		item["email"] = row[1]
		item["link"] = row[2]			
		item["fullname"] = row[3]
		item["description"] = row[4]
		item["id"] = row[5]
		item["gravatar"] = get_gravatar_url(item["email"],96)
		items.append(item)
				
	return template('user/list',
		userinfo=userinfo, 
		message=message,
		items=items,
		is_admin=is_admin(userinfo))

@app.route('/signup')
def signup(db):
	userinfo = is_logged_in(db)
	return template('user/signup',
		userinfo = False,
		username="", message="", email="", link="")	
            
@app.route('/signup',method="POST")
def do_signup(db):
	userinfo = is_logged_in(db)
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
	else:	
		c = db.execute('select id, password from users where username = "%s"' % (submitted_username))
		row = c.fetchone()
		if row:
			error = True
			message.append("Username exists.")				
		
	if len(submitted_username) < 3 or len(submitted_username) > 15:
		error = True
		message.append("Username has to be between 3 and 15 characters long")

	if len(submitted_email) < 1:
		error = True
		message.append("E-Mail is required")
		
	else:
		c = db.execute('select id from users where email = "%s"' % (submitted_email))
		row = c.fetchone()
		if row:
			error = True
			message.append("E-Mail already registered")			
		
	if len(submitted_password) < 1:
		error = True
		message.append("A Password is required")
		
	if submitted_password != submitted_confirm_password:
		error = True
		message.append("Passwords do not match")
		
				
	if not error:	
		password = crypt.crypt(submitted_password,salt)
		c = db.execute('insert into users (username, email, password, link) values (?, ?, ?, ?)', 
			(submitted_username, submitted_email, password, submitted_link))
		redirect("/login")
		
	else:
		return template('user/signup', 
			userinfo=userinfo,
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
			
	if userinfo:
		if username == userinfo["username"]:
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
			gravatar_large=get_gravatar_url(email,96),
			is_me=is_me,
			is_admin=is_admin(userinfo),
			message="", header="")	


@app.route('/edit_profile')
def profile_edit(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	
	c = db.execute('''select 
			email, link, fullname, description  
		from users where username = "%s"'''
		 % (userinfo["username"]))
		 
	(email,link,fullname, description) = c.fetchone()	

	if description == None:
		description = ""
		
	if fullname == None:
		fullname = ""		
		
	return template('user/edit_profile',
		userinfo=userinfo, 
		fullname=fullname,
		description= description,
		message="", 
		email=email, link=link)	
            
@app.route('/edit_profile',method="POST")
def profile_update(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	is_me = True
	submitted_link = request.forms.get('link')
	submitted_email = request.forms.get('email')
	submitted_fullname = request.forms.get('fullname').decode("utf-8")
	submitted_description = request.forms.get('description').decode("utf-8")

	message = []
	error = False
	
	if len(submitted_email) < 1:
		error = True
		message.append("E-Mail is required")
		
	if len(submitted_email) > 50:
		error = True
		message.append("E-Mail too long")
				
	if not error:	
		c = db.execute('update users set email=?, link=?, description=?, fullname=? where username =?',
			(submitted_email, 
			submitted_link, 
			submitted_description.decode('utf8'), 
			submitted_fullname.decode('utf8'),
			userinfo["username"]))
			
		message = "Your profile was updated"
		gravatar_url = get_gravatar_url(submitted_email)
		
		redirect("/profile/"+userinfo["username"])
		
	else:		
		return template('user/edit_profile', 
			userinfo=userinfo,
			message=message, 
			link=submitted_link,
			description=submitted_description,
			fullname = submitted_fullname,
			email=submitted_email)

@app.route('/profile/edit/<uid>')
def profile_edit_admin(db,uid):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		return render_error(db,"Not allowed")
	
	c = db.execute('''select 
			email, link, fullname, description, id, username 
		from users where id = "%s"'''
		 % (uid))
		 
	(email,link,fullname, description,user_id,user_name) = c.fetchone()	

	if description == None:
		description = ""
		
	if fullname == None:
		fullname = ""		
		
	return template('user/edit_admin',
		userinfo=userinfo, 
		fullname=fullname,
		description= description,
		user_id=user_id, user_name=user_name,
		message="", 
		email=email, link=link)	

@app.route('/profile/edit/<uid>',method="POST")
def profile_update_admin(db, uid):
	userinfo = is_logged_in(db)
	if not is_admin(userinfo):
		return render_error(db,"Not allowed")
	is_me = True
	user_name = request.forms.get('user_name')
	submitted_link = request.forms.get('link')
	submitted_email = request.forms.get('email')
	submitted_fullname = request.forms.get('fullname').decode("utf-8")
	submitted_description = request.forms.get('description').decode("utf-8")
	submitted_password = request.forms.get('password')
	submitted_confirm_password = request.forms.get('confirm_password')	
	
	message = []
	error = False
	has_password = False
	
	if len(submitted_email) < 1:
		error = True
		message.append("E-Mail is required")
		
	if len(submitted_email) > 50:
		error = True
		message.append("E-Mail too long")
		
	if len(submitted_password) > 0 and len(submitted_password) < 4:
		error = True
		message.append("Password is too short (min. 4 chars")
	
	else:
		if len(submitted_password) > 4:
			has_password = True
			if len(submitted_password) > 15:
				error = True
				message.append("Password is too long (max. 15 chars")
					
			if submitted_password != submitted_confirm_password:
				error = True
				message.append("Passwords do not match")			
				
	if not error:	
		if has_password:
			password = crypt.crypt(submitted_password,salt)	
			c = db.execute('update users set email=?, link=?, description=?, fullname=?, password=? where id =?',
				(	submitted_email, 
					submitted_link, 
					submitted_description.decode('utf8'), 
					submitted_fullname.decode('utf8'),
					password,
					uid
				))
		else:
			c = db.execute('update users set email=?, link=?, description=?, fullname=? where id =?',
				(	submitted_email, 
					submitted_link, 
					submitted_description.decode('utf8'), 
					submitted_fullname.decode('utf8'),
					uid
				))			
			
		message = {}
		message["title"]  = "Success"
		message["text"]  = "User updated %s " % (user_name)
			
		return profiles_list(db,message);
		
	else:		
		return template('user/edit_admin', 
			userinfo=userinfo,
			user_id=uid,
			user_name=user_name,
			message=message, 
			link=submitted_link,
			description=submitted_description,
			fullname = submitted_fullname,
			email=submitted_email)


@app.route('/profile/delete/<uid>')
def profile_delete(db,uid):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
	
	
	c = db.execute('''select 
			username, id 
		from users where id = "%s"'''
		 % (uid))
		
	item = {}
	(item["username"],item["id"]) = c.fetchone()	
		
	return template('user/delete',
		userinfo=userinfo, 
		item=item,
		message="")	
		
@app.route('/profile/delete/<uid>',method="POST")
def profile_do_delete(db,uid):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	if not is_admin(userinfo):
		return render_error(db,"NOT ALLOWED")
	
	c = db.execute('''delete from designs where user_id = "%s"'''
		 % (uid))
	c = db.execute('''delete from users where id = "%s"'''
		 % (uid))
		
	message = {}
	message["title"]  = "Deleted"
	message["text"]  = "delete user id %s " % (uid)
		
	return profiles_list(db,message);
            		

@app.route('/change_password')
def password_change(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")
	return template('user/change_password', userinfo=userinfo, message="", email="", link="")	
            
@app.route('/change_password',method="POST")
def password_update(db):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"Not logged in")	
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

########################################################
# drawings 
#########################################################
## this is a addon not directly connected to turtlestitch

drawing_abs_path = "%s/%s" % (upload_abs_path, "drawings")
drawing_www_path = "%s/%s" % (upload_www_path, "drawings")

@app.route('/draw')
def draw(db):
	userinfo = is_logged_in(db)
	return template('draw/draw', 
		draw_active='active',
		userinfo=userinfo)
	
@app.route('/draw/upload',method='post')
def draw_upload(db):
	ii = 0
	points = request.POST.getlist("points[]")
	types = request.POST.getlist("ptypes[]")
	name = request.POST.get('name').decode("utf-8")
	
	if not os.path.exists(drawing_abs_path):
		os.makedirs(drawing_abs_path)			
	
	if len(points) > 1:
		pixels_per_millimeter = 10
		emb = stitchcode.Embroidery()
		lx = -99999999
		ly = -99999999
		fid = str(int(time.time() * 1000))
		
		for ppoint in points:		
			x = float(ppoint.split(",")[0].split(":")[1])
			y = -float(ppoint.split(",")[1].split(":")[1][:-2])
			if types[ii] == "true": 
				jump = True;
			else:
				jump = False
			emb.addStitch(stitchcode.Point(x,y,jump))	
					
		emb.translate_to_origin()	
		emb.scale(27.80/pixels_per_millimeter)
		emb.flatten()
		emb.add_endstitches_to_jumps(10)
		emb.save_as_exp("%s/%s.exp" % (drawing_abs_path,fid) )	
		x,y = emb.getSize()
	
		if x*y < 4000000:
			emb.save_as_png("%s/%s.png" % (drawing_abs_path,fid), True)
		else:
			print "image to big: %dx%d = %d" % (x,y,x*y)
			return "ERROR"	
			
		userinfo = is_logged_in(db) 
		if not userinfo:
			userid=0
		else:
			userid=userinfo["id"]
			
		if name:
			title = name
		else:
			title = fid
					
		c = db.execute(
			'insert into drawings (id, title, user_id, description) values(?, ?, ?,"")', 
			(fid, title, userid))
		db.commit()
			
		return "OK:%s" % (fid)
	else:
		return "ERROR"
		
		
###################        
# draw view detail
###################    
@app.route('/draw/view/<gid>')
def draw_view(db,gid=0,message=False):
	userinfo = is_logged_in(db)

	c = db.execute('''select 
					drawings.id, drawings.title, drawings.description, 
					users.username 
				from drawings left outer join users
				on drawings.user_id = users.id 
				where drawings.id = ?''',(gid,))
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
	item["dst_file"] = "%s.dst" % (item["id"])
	item["svg_file"] = "%s.svg" % (item["id"])
	item["pes_file"] = "%s.pes" % (item["id"])
	item["media_path"] = drawing_www_path	
	item["url"] =  request.url 
	
	
	if not os.path.isfile("%s/%s" % (drawing_abs_path, item["exp_file"])):
		return render_error(db,"File does not exist");

	if not os.path.isfile("%s/%s" % (drawing_abs_path, item["svg_file"])):
		emb = stitchcode.Embroidery()
		emb.import_melco("%s/%s" % (drawing_abs_path, item["exp_file"]))
		emb.scale(1.0)
		emb.save_as_svg("%s/%s" % (drawing_abs_path, item["svg_file"]))		

	if not os.path.isfile("%s/%s" % (drawing_abs_path, item["dst_file"])):
		emb = stitchcode.Embroidery()
		emb.import_melco("%s/%s" % (drawing_abs_path, item["exp_file"]))
		emb.scale(1.0)
		emb.save_as_dst("%s/%s" % (drawing_abs_path, item["dst_file"]))	

		
	return template('draw/view', 
		item=item, userinfo=userinfo,
		message=message,
		is_admin = is_admin(userinfo),
		gallery_active="active") 	
							


@app.route('/draw/gallery')
@app.route('/draw/featured')
@app.route('/draw/featured/<page>')
def draw_featured(db,page=1,featured=False,textile=False):
	return draw_list(db,page=page,featured=True,textile=False)
		
@app.route('/draw/list')
@app.route('/draw/all')
@app.route('/draw/page/<page>')
def draw_list(db,page=1,featured=False,textile=False):
	userinfo = is_logged_in(db)

	page_link = "/draw/list/"
	query = '''select 
			drawings.id, drawings.title, drawings.description, 
			users.username 
		from drawings left outer join users
		on drawings.user_id = users.id
		order by drawings.timestamp desc'''
	if featured:
		page_link = "/draw/featured"
		query = '''select 
			drawings.id, drawings.title, drawings.description, 
			users.username 
		from drawings 
		left outer join users
		on drawings.user_id = users.id where drawings.featured = 1 
		order by drawings.timestamp desc'''
	if textile:
		page_link = "/draw/textile"
		query = '''select 
				designs.id, designs.title, designs.description, users.username,
				designs_images.name 
			from designs 
			left join users on designs.user_id=users.id 
			left join designs_images on designs_images.design_id=designs.id 
			where  designs_images.name != ""
			order by designs.timestamp desc'''
	c = db.execute(query)
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
		
		if textile:
			item["png_file"] = "%s/%s/%s" % ("images",row[0],row[4])
			
		item["exp_file"] = "%s.exp" % (row[0])
		item["media_path"] = drawing_www_path
		if i >= start and i <= stop:
			items.append(item)
		i += 1		
	
	return template('draw/list',
		items=items, userinfo=userinfo, page=page, pages=num_pages,
		total=num_files, 
		featured=featured,
		page_link=page_link,
		textile=textile,
		is_admin = is_admin(userinfo),
		gallery_active="active")    	


###################        
# drawing edit
###################    
@app.route('/draw/edit/<gid>')
def draw_edit(db,gid=0):	
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")
		
	c = db.execute('''select 
					drawings.id, drawings.title, drawings.description, 
					users.username, users.id, drawings.featured
				from drawings left outer join users
				on drawings.user_id = users.id 
				where drawings.id = ?''',(gid,))
	row = c.fetchone()

	if not row:
		return render_error(db,"File does not exist");	    

	item = {}
	item["id"] = row[0]
	item["title"] = row[1]			
	item["description"] = row[2]
	item["owner"] = row[3]
	item["owner_id"] = row[4]
	if row[5]>0:
		item["featured"] = "checked"
	else:
		item["featured"] = ""
		
	item["is_owner"] = (row[3] == userinfo["username"])
	if not item["is_owner"] and not userinfo["is_admin"]:
		return render_error(db,"NOT ALLOWED");	  
				
	item["png_file"] = "%s.png" % (item["id"])
	item["exp_file"] = "%s.exp" % (item["id"])
	item["svg_file"] = "%s.svg" % (item["id"])
	item["pes_file"] = "%s.pes" % (item["id"])
	item["media_path"] = drawing_www_path	
	item["url"] =  request.url 
	
	return template('draw/edit', 
		item=item, userinfo=userinfo,
		is_admin=is_admin(userinfo),
		gallery_active="active") 
		
@app.route('/draw/update/<gid>', method='POST')
def draw_update(db,gid=0):
	userinfo = is_logged_in(db)
	submitted_title = request.forms.get('title').decode("utf-8")
	submitted_description = strip_tags(request.forms.get('description')).decode("utf-8")
	submitted_owner_id = request.forms.get('owner_id')
	submitted_featured = request.forms.get('featured')
	if submitted_featured == None:
		submitted_featured = 0

	c = db.execute('select user_id from drawings where id = ?', (gid,))
	row = c.fetchone()
	
	if not row:
		return render_error(db,"File does not exist");

	if row[0] != userinfo["id"] and not is_admin(userinfo):
		return render_error(db,"Not allowed");
	
	if is_admin(userinfo):
		c = db.execute('update drawings set title = ?, description = ?, user_id = ?, featured = ? where id = ?', 
				(submitted_title, submitted_description, submitted_owner_id, submitted_featured, gid ))
	else:
		c = db.execute('update drawings set title = ?, description = ? where id = ?', 
				(submitted_title, submitted_description, gid))
	db.commit()
	message = "Your item was changed."	

	return draw_view(db,gid,message)
	

@app.route('/draw/delete/<gid>')
def gallery_delete(db,gid=0):
	userinfo = is_logged_in(db)
	if not userinfo:
		return render_error(db,"NOT ALLOWED")

	c = db.execute('''select user_id 
				from drawings 
				where id = ?''',(gid,))
	row = c.fetchone()
	if not row:
		return render_error(db,"File does not exist");
	else:
		if row[0] == userinfo["id"] or userinfo["is_admin"]:
			c = db.execute('delete from drawings where id=?',(gid,))
			files = images = glob.glob("%s/%s.*" % (drawing_abs_path,gid));
			for f in files:
				os.unlink(f)
			redirect("/draw/gallery")
		else:
			return render_error(db,"NOT ALLOWED")	
			

###################################################
# helper function 
####################################################

def render_error(db,string):
	userinfo = is_logged_in(db)	
	return template('error', 
		userinfo=userinfo, 
		message=string,  
		message_header="Error")
		
def render_success(db,string):
	userinfo = is_logged_in(db)	
	return template('success', 
		userinfo=userinfo, 
		message=string,  
		message_header="Success")		
		
def render_message(db,string,header=""):
	userinfo = is_logged_in(dnb)	
	return template('message', 
		userinfo=userinfo, 
		message=string,  
		message_header=header)		


def get_host():
	return "%s%s" % ("http://", request.urlparts[1])

def get_gravatar_url(email,size=24):
	default = "%s/media/img/%s" % (get_host(), "turtle.png") 
	gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
	gravatar_url += urllib.urlencode({'d':default, 's':str(size)})	
	#gravatar_url += urllib.urlencode({'s':str(size)})	
	return gravatar_url
	
	
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()	


def send_mail(to, sender, subject, body):
    sendmail_location = "/usr/sbin/sendmail" # sendmail location
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % sender)
    p.write("To: %s\n" % to)
    p.write("Subject:"+ subject + "\n")
    p.write("\n") # blank line separating headers from body
    p.write(body)
    status = p.close()
    if status != 0:
           print "Sendmail exit status", status


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
