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
        
        #if we get a false delivery solution, it's basically useless
        #so we need to remove the false deliveries and try to solve again
        #and then put them back into the pickups_deliveries list
        def except_false_delivery(solution,loc_coord_list, plane_coord_list, pickups_deliveries, 
            pickups_deliveries_in_progress):
            if solution['false_deliveries']:
                dropped_deliveries = solution['false_deliveries'].copy()
                for false_delivery in solution['false_deliveries']:
                    solution['pickups_deliveries'].remove(false_delivery)
                
                #solve without the error causing delivery requests
                new_solution = solve(loc_coord_list, plane_coord_list, pickups_deliveries, 
                    pickups_deliveries_in_progress)

                #add the deliveries we removed back into the to-do list
                new_solution['pickups_deliveries'] += dropped_deliveries

                return new_solution
            else:
                return solution

        MAX_CHECKS_CONST = 10
        #try to fix the 'false' solutions 
        for i in range(MAX_CHECKS_CONST):
            solution = except_false_delivery(solution,loc_coord_list, 
                plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress)
            

            

        return solution

#add this resource(class) to the default directory
api.add_resource(RouteManager, "/")


if __name__ == "__main__":
    app.run(debug=True)