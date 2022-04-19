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
                         "creation_date": content["creation_date"], "carrier": [], "self": None})
        client.put(new_load)
        self = request.base_url + '/' + str(new_load.key.id)
        new_load.update({"self": self})
        client.put(new_load)
        return {"id": new_load.key.id, "volume": content["volume"], "item": content["item"],
                "creation_date": content["creation_date"], "carrier": [], "self": self}, 201
    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results), 200
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

    # if request.method == 'POST':
    #     content = request.get_json()
    #     new_guest = datastore.entity.Entity(key=client.key(constants.loads))
    #     new_guest.update({"name": content["name"]})
    #     client.put(new_guest)
    #     return str(new_guest.key.id)
    # elif request.method == 'GET':
    #     query = client.query(kind=constants.loads)
    #     q_limit = int(request.args.get('limit', '2'))
    #     q_offset = int(request.args.get('offset', '0'))
    #     g_iterator = query.fetch(limit= q_limit, offset=q_offset)
    #     pages = g_iterator.pages
    #     results = list(next(pages))
    #     if g_iterator.next_page_token:
    #         next_offset = q_offset + q_limit
    #         next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
    #     else:
    #         next_url = None
    #     for e in results:
    #         e["id"] = e.key.id
    #     output = {"guests": results}
    #     if next_url:
    #         output["next"] = next_url
    #     return json.dumps(output)


@bp.route('/<id>', methods=['GET', 'DELETE'])
def loads_put_delete(id):
    if request.method == 'DELETE':
        key = client.key(constants.loads, int(id))
        load_key = client.get(key=key)
        if load_key is None:
            return {"Error": "No boat with this boat_id exists"}, 404
        # query = client.query(kind=constants.slips)
        # results = list(query.add_filter('current_boat', '=', int(id)).fetch())
        # if results:
        #     slip_key = client.key(constants.slips, results[0].key.id)
        #     slip = client.get(key=slip_key)
        #     slip.update({"current_boat": None})
        #     client.put(slip)
        client.delete(key)  
        return '', 204
    elif request.method == 'GET':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load is None:
            return {"Error": "No boat with this boat_id exists"}, 404
        load["id"] = load.key.id
        return json.dumps(load), 200
    else:
        return 'Method not recognized'
