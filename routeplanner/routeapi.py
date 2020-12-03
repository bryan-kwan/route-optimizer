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
        pickups_deliveries_queue = args['pickups_deliveries_queue']


        #calculate optimized route as a json
        solution = solve(loc_coord_list, plane_coord_list, pickups_deliveries, 
                    pickups_deliveries_in_progress, pickups_deliveries_queue)
        
        #if we get a false delivery solution, it's basically useless
        #so we need to move the deliveries that cause a false solution into queue
        #then solve again
        def except_false_delivery(solution,loc_coord_list, plane_coord_list, pickups_deliveries, 
                    pickups_deliveries_in_progress, pickups_deliveries_queue):
            if solution['false_deliveries']:
                for false_delivery in solution['false_deliveries']:
                    solution['pickups_deliveries_queue'].append(false_delivery)
                    solution['pickups_deliveries'].remove(false_delivery)

                #solve without the error causing delivery requests
                new_solution = solve(loc_coord_list, plane_coord_list, pickups_deliveries, 
                    pickups_deliveries_in_progress, pickups_deliveries_queue)

                return new_solution
            else:
                return solution

        #sometimes there's no solution with the given constraints
        def except_no_solution(solution,loc_coord_list, plane_coord_list, pickups_deliveries, 
            pickups_deliveries_in_progress, pickups_deliveries_queue):
            if solution is None:
                #try moving pickups_deliveries to queue until there is a solution
                delivery = solution['pickups_deliveries'][0]
                solution['pickups_deliveries_queue'].append(delivery)
                solution['pickups_deliveries'].remove(delivery)
                #put into the solver
                new_solution = solve(loc_coord_list, plane_coord_list, pickups_deliveries, 
                    pickups_deliveries_in_progress, pickups_deliveries_queue)
                
                return new_solution
            else:
                return solution
                

        MAX_CHECKS_CONST = 10
        for i in range(MAX_CHECKS_CONST):
            #try to fix the no solutions
            solution = except_no_solution(solution,loc_coord_list, 
                plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress, pickups_deliveries_queue)
            #try to fix the 'false' solutions 
            solution = except_false_delivery(solution,loc_coord_list, 
                plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress, pickups_deliveries_queue)
            
            

        return solution

#add this resource(class) to the default directory
api.add_resource(RouteManager, "/")


if __name__ == "__main__":
    app.run(debug=True)