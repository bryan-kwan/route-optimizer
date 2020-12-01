#used this tutorial https://www.youtube.com/watch?v=GMppyAPbLYk

from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

#request parser 
#assuming we're going to just take in a json from the database
route_put_args = reqparse.RequestParser()
route_put_args.add_argument("data", type = json, 
    help='''Requires Data from database: location/plane coordinates and pickup_delivery requests''',
    required=True)     


from routecalculator import solve

#just holds the info we want to return, etc.
class RouteManager(Resource):
    def get(self):
        #we have to read values from the database to calculate the route
        args = route_put_args.parse_args()
        #python interprets the json as a dictionary  #probably... lol
        loc_coord_list = args['loc_coord_list']
        plane_coord_list = args['plane_coord_list']
        pickups_deliveries = args['pickups_deliveries'] 
        pickups_deliveries_in_progress = args['pickups_deliveries_in_progress'] 


        #calculate optimized route as a json
        solution = solve(loc_coord_list, plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress)
        
        return solution

#add this resource(class) to the default directory
api.add_resource(RouteManager, "/")


if __name__ == "__main__":
    app.run(debug=True)