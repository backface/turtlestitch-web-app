import os, sys

# Change working directory so relative paths (and template lookup) work again
sys.path.append(os.path.dirname(__file__))

import bottle

# ... build or import your bottle application here ...
# Do NOT use bottle.run() with mod_wsgi
#application = bottle.default_app()

app = bottle.default_app()
bottle.TEMPLATE_PATH.insert(0,'/home/mash/data/projects/stitchcode/turtlestitch-web-app/app/views/')

#application = app
from turtlestitch import application


