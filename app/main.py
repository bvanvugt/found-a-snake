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

    life = data['you']['health']
    head_coords = data['you']['body'][0]

    up_coords = head_coords.copy()
    up_coords['y'] = head_coords['y'] - 1

    down_coords = head_coords.copy()
    down_coords['y'] = head_coords['y'] + 1

    left_coords = head_coords.copy()
    left_coords['x'] = head_coords['x'] - 1

    right_coords = head_coords.copy()
    right_coords['x'] = head_coords['x'] + 1

    if life <= (max(data['board']['width'], data['board']['height']) * 2):
        print "TRY TO EAT!"
        nearest_food_coords = get_nearest_food(head_coords, data['board'])
        
        if nearest_food_coords:
            if nearest_food_coords['x'] < head_coords['x']:
                if is_safe(head_coords['x'] - 1, head_coords['y'], data['board']):
                    return MoveResponse('left')
            elif nearest_food_coords['x'] > head_coords['x']:
                if is_safe(head_coords['x'] + 1, head_coords['y'], data['board']):
                    return MoveResponse('right')
            elif nearest_food_coords['y'] < head_coords['y']:
                if is_safe(head_coords['x'], head_coords['y'] - 1, data['board']):
                    return MoveResponse('up')
            elif nearest_food_coords['y'] > head_coords['y']:
                if is_safe(head_coords['x'], head_coords['y'] + 1, data['board']):
                    return MoveResponse('down')

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


def get_nearest_food(head, board):
    if len(board['food']) == 0:
        return None
    
    distances = [
        (i, abs(head['x'] - f['x']) + abs(head['y'] - f['y']))
        for i, f in enumerate(board['food'])
    ]
    distances.sort(key=lambda x: x[1])
    
    nearest_food_coords = board['food'][distances[0][0]]
    print "TARGET FOOD:", nearest_food_coords
    return nearest_food_coords


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
