from flask import Blueprint, request
from google.cloud import datastore
import json
from json2html import *
import constants

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix='/loads')


# ***** REMEmBER to DELETE DELETE ******
@bp.route('', methods=['POST', 'GET', 'DELETE'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if len(content) < 3:
            return {"Error": "The request object is missing at least one of the required attributes"}, 400
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({"volume": content["volume"], "item": content["item"],
                         "creation_date": content["creation_date"], "carrier": None})
        client.put(new_load)
        self = request.base_url + '/' + str(new_load.key.id)
        return {"id": new_load.key.id, "volume": content["volume"], "item": content["item"],
                "creation_date": content["creation_date"], "carrier": None, "self": self}, 201
    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit=q_limit, offset=q_offset)
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
            if e["carrier"] is not None:
                e["carrier"]["self"] = request.host_url + 'boats/' + str(e["carrier"]["id"])
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output), 200
    elif request.method == 'DELETE':
        query = client.query(kind=constants.loads)
        results = list(query.fetch())
        for e in results:
            key = e.key.id
            c_key = client.key(constants.loads, int(key))
            print(c_key)
            client.delete(c_key)
        return '', 204
    else:
        return 'Method not recognized'


@bp.route('/<id>', methods=['GET', 'DELETE'])
def loads_get_delete(id):
    if request.method == 'DELETE':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load is None:
            return {"Error": "No load with this load_id exists"}, 404
        boat_key = client.key(constants.boats1, int(load['carrier']['id']))
        boat = client.get(key=boat_key)
        for i in boat['loads']:
            if i['id'] == int(id):
                boat['loads'].remove(i)
                client.put(boat)
        client.delete(load_key)
        return '', 204
    elif request.method == 'GET':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load is None:
            return {"Error": "No load with this load_id exists"}, 404
        load["id"] = load.key.id
        load["self"] = request.host_url + 'loads/' + str(load["id"])
        if load["carrier"] is not None:
            load["carrier"]["self"] = request.host_url + 'boats/' + str(load["carrier"]["id"])
        return json.dumps(load), 200
    else:
        return 'Method not recognized'
