import bottle
import os
import random

from api import *


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    print "Starting game %s" % data["game"]["id"]
    return StartResponse("#00ff00")


@bottle.post('/move')
def move():
    data = bottle.request.json

    board_max_x = data['board']['width']
    board_max_y = data['board']['height']

    head_coords = data['you']['body'][0]   

    diff_x = board_max_x - head_coords['x']
    diff_y = head_coords['y']

    if diff_x > diff_y:
        return MoveResponse('right')
    if diff_y > diff_x:
        return MoveResponse('up')
    return MoveResponse(random.choice(['up', 'right']))


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    print "Game %s ended" % data["game"]["id"]


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
