from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boats1', __name__, url_prefix='/boats')


# ***** REMEmBER to DELETE DELETE ******
@bp.route('', methods=['POST', 'GET', 'DELETE'])
def boats_get_post1():
    if request.method == 'POST':
        content = request.get_json()
        if len(content) < 3:
            return {"Error": "The request object is missing at least one of the required attributes"}, 400
        new_boat = datastore.entity.Entity(key=client.key(constants.boats1))
        new_boat.update({"name": content["name"], "type": content["type"],
                         "length": content["length"], "loads": []})
        client.put(new_boat)
        self = request.base_url + '/' + str(new_boat.key.id)
        return {"id": new_boat.key.id, "name": content["name"], "type": content["type"],
                "length": content["length"], "loads": [], "self": self}, 201
    elif request.method == 'GET':
        query = client.query(kind=constants.boats1)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
            e["self"] = request.base_url + '/' + str(e["id"])
            for i in e["loads"]:
                i["self"] = request.host_url + 'loads/' + str(i["id"])
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output), 200
    elif request.method == 'DELETE':
        query = client.query(kind=constants.boats1)
        results = list(query.fetch())
        for e in results:
            key = e.key.id
            c_key = client.key(constants.boats1, int(key))
            print(c_key)
            client.delete(c_key)
        return '', 204
    else:
        return 'Method not recognized'


@bp.route('/<id>', methods=['GET', 'DELETE'])
def boats_get_delete(id):
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats1, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return {"Error": "No boat with this boat_id exists"}, 404
        for i in boat['loads']:
            load_key = client.key(constants.loads, int(i['id']))
            load = client.get(key=load_key)
            load['carrier'] = None
            client.put(load)
        client.delete(boat_key)
        return '', 204
    elif request.method == 'GET':
        boat_key = client.key(constants.boats1, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return {"Error": "No boat with this boat_id exists"}, 404
        boat["id"] = boat.key.id
        boat["self"] = request.host_url + 'boats/' + str(boat["id"])
        if len(boat["loads"]) != 0:
            for i in boat["loads"]:
                i["self"] = request.host_url + 'loads/' + str(i["id"])
        return json.dumps(boat), 200
    else:
        return 'Method not recognized'


@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def add_delete_load_to_boat(boat_id, load_id):
    if request.method == 'PUT':
        boat_key = client.key(constants.boats1, int(boat_id))
        boat = client.get(key=boat_key)  
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)
        if (boat is None) or (load is None):
            return {"Error": "The specified boat and/or load does not exist"}, 404
        if load['carrier'] is not None:
            return {"Error": "The load is already loaded on another boat"}, 403
        boat['loads'].append({"id": load.id})
        load['carrier'] = {"id": boat.id}
        client.put(boat)
        client.put(load)
        return ('', 204)
    if request.method == 'DELETE':
        load_on_boat = False
        boat_key = client.key(constants.boats1, int(boat_id))
        boat = client.get(key=boat_key)
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)
        if (boat is None) or (load is None):
            return {"Error": "No boat with this boat_id is loaded with the load with this load_id"}, 404
        for i in boat['loads']:
            if i['id'] == int(load_id):
                load_on_boat = True
                boat['loads'].remove(i)
        if load_on_boat is False:
            return {"Error": "No boat with this boat_id is loaded with the load with this load_id"}, 404
        load['carrier'] = None
        client.put(boat)
        client.put(load)
        return ('', 204)


@bp.route('/<boat_id>/loads', methods=['GET'])
def get_reservations(boat_id):
    boat_key = client.key(constants.boats1, int(boat_id))
    boat = client.get(key=boat_key)
    if boat is None:
        return {"Error": "No boat with this boat_id exists"}, 404
    load_dict = {'loads': []}
    for i in boat['loads']:
        load_key = client.key(constants.loads, int(i['id']))
        load = client.get(key=load_key)
        load["self"] = request.host_url + 'loads/' + str(i["id"])
        load["id"] = i['id']
        load_dict['loads'].append(load)
    return json.dumps(load_dict), 200
