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
    return StartResponse("#f4741d")


@bottle.post('/move')
def move():
    data = bottle.request.json

    board_max_x = data['board']['width']
    board_max_y = data['board']['height']

    head_coords = data['you']['body'][0]

    up_coords = head_coords.copy()
    up_coords['y'] = head_coords['y'] - 1

    down_coords = head_coords.copy()
    down_coords['y'] = head_coords['y'] + 1

    left_coords = head_coords.copy()
    left_coords['x'] = head_coords['x'] - 1

    right_coords = head_coords.copy()
    right_coords['x'] = head_coords['x'] + 1

    desired = ['up', 'right']
    random.shuffle(desired)
    for move in desired:
        if move == 'up' and is_safe(up_coords['x'], up_coords['y'], data['board']):
            return MoveResponse('up')
        if move == 'right' and is_safe(right_coords['x'], right_coords['y'], data['board']):
            return MoveResponse('right')
    
    # Okay if we have to
    desired = ['left', 'down']
    random.shuffle(desired)
    for move in desired:
        if move == 'left' and is_safe(left_coords['x'], left_coords['y'], data['board']):
            return MoveResponse('left')
        if move == 'down' and is_safe(down_coords['x'], down_coords['y'], data['board']):
            return MoveResponse('down')

    
    print "FALL THROUGH"
    return MoveResponse('down')


    # print head_coords
    # print right_coords
    # print left_coords
    # return MoveResponse('right')

    # diff_x = board_max_x - 1 - head_coords['x']
    # diff_y = head_coords['y']

    # in_top_right = any([
    #     (b['x'] == (board_max_x - 1) and b['y'] == 0)
    #     for b in data['you']['body']
    # ])

    # print "Board:", board_max_x, board_max_x
    # print "Head: ", head_coords['x'], head_coords['y']
    # print "Diff: ", diff_x, diff_y
    # print "TopR: ", in_top_right
    
    # if in_top_right:
    #     can_go_down = not any([
    #         (b['x'] == (board_max_x - 1) and b['y'] == 1)
    #         for b in data['you']['body']
    #     ])
    #     if can_go_down:
    #         return MoveResponse('down')
        
    #     can_go_left = not any([
    #         (b['x'] == (board_max_x - 2) and b['y'] == 0)
    #         for b in data['you']['body']
    #     ])
    #     if can_go_left:
    #         return MoveResponse('left')
        
    #     if head_coords['x'] > board_max_x - 2:
    #         return MoveResponse('left')
    #     if head_coords['y'] < 1:
    #         return MoveResponse('down')

    # if diff_x > diff_y:
    #     return MoveResponse('right')
    # if diff_y > diff_x:
    #     return MoveResponse('up')
    # return MoveResponse(random.choice(['up', 'right']))


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    print "Game %s ended" % data["game"]["id"]


def is_safe(x, y, board):
    if x < 0 or x >= board['width']:
        return False
    if y < 0 or y >= board['height']:
        return False
    
    for snake in board['snakes']:
        for body in snake['body']:
            if body['x'] == x and body['y'] == y:
                return False
    
    return True



# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
