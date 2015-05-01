# -*- coding: UTF-8 -*-
__author__ = 'skwek'
import cherrypy
import redis
import json
import sys

class PriceLookup():
    def __init__(self, redis_host, redis_port_number=6379):
        self._r_server = redis.Redis(redis_host, redis_port_number)

    @staticmethod
    def _to_float(int_str):
        try:
            value = float(int_str)
            return value
        except:
            print "Unable to convert {0} to float".format(int_str)
            return None

    @cherrypy.expose
    def lookup(self, product_id_composite, redis_keys=None, old_price=None):
        response = {}

        best_price = sys.float_info.max
        item_price = PriceLookup._to_float(self._r_server.get('price:' + product_id_composite))
        if item_price:
            best_price = item_price
            response['item_price'] = item_price
            response['item_found'] = True
        else:
            response['item_found'] = False
        print product_id_composite, item_price, best_price

        if redis_keys is not None:
            cheaper_local_item = None
            for key in redis_keys.split(','):
                if key != product_id_composite:
                    price = PriceLookup._to_float(self._r_server.get('price:' + key))
                    print key, price, best_price
                    if price is not None and price < best_price:
                        best_price = price
                        cheaper_local_item = key

            if cheaper_local_item is not None:
                response['better_price'] = best_price
                response['cheaper_product_id_composite'] = key
        return json.dumps(response)

    @staticmethod
    def start(redis_host='localhost'):
        conf = {
            '/': {
                'tools.sessions.on': True,
                'server.max_request_body_size': 0
            }
        }
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8109,
            'server.max_request_body_size': 0
        })
        cherrypy.quickstart(PriceLookup(redis_host), '/', conf)

if __name__ == "__main__":
    PriceLookup.start()



