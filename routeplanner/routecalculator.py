#cvrp theory https://arxiv.org/pdf/1606.01935.pdf
#solution modified from https://developers.google.com/optimization/routing


"""Simple Pickup Delivery Problem (PDP)."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from datamodel import create_data_model, create_data_model_sample



#needs to output the following lists:
    #1 route
    #2 load (at each node)
    #3 distance of each route
    #4 dropped nodes --> find out the dropped requests from here --> need to recalculate for feasible solution
    #4.5 remaining set of requests (these will be the dropped requests)
    #5 total distance of all routes
class RouteSolution():

    def get_solution(self, data, manager, routing, solution):
        #get dropped nodes
        self.dropped_nodes_list = []
        self.pickups_deliveries_list_unfinished = []
        self.pickups_deliveries_list_not_started = []
        self.pickups_deliveries_list_false_delivery = []
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                self.dropped_nodes_list.append(manager.IndexToNode(node))

        #finds dropped requests from the dropped nodes
        for request in data['pickups_deliveries']:
            #checks if we drop the dropoff but not the pickup 
            #ie an unfinished delivery
            if ((request[1] in self.dropped_nodes_list) and (request[0] not in self.dropped_nodes_list)):
                self.pickups_deliveries_list_unfinished.append(request)

            #checks if we drop both dropoff and pickup
            #ie a delivery not started
            elif ((request[1] in self.dropped_nodes_list) and (request[0] in self.dropped_nodes_list)):
                self.pickups_deliveries_list_not_started.append(request)

            #checks if we drop the pickup but not the dropoff
            #calling these false deliveries
            elif ((request[0] in self.dropped_nodes_list) and (request[1] not in self.dropped_nodes_list)):
                self.pickups_deliveries_list_false_delivery.append(request)



        #get routes
        self.total_distance = 0
        self.total_load = 0

        capacity_dimension = routing.GetDimensionOrDie('Capacity')
        delivery_dimension = routing.GetDimensionOrDie('Delivery')
        
        self.route_list = []
        self.load_list = []
        self.total_distance_each_route_list = []
        self.pickups_deliveries_completed = []

        #calculate routes for each vehicle
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            
            route_distance = 0
            route_load = 0

            self.route_node_list = []
            self.route_load_list = []
            #checks until we hit the end of the route
            while not routing.IsEnd(index):

                route_load += data['demands'][manager.IndexToNode(index)]

                self.route_node_list.append(manager.IndexToNode(index))
                self.route_load_list.append(route_load)

                #check if we completed a delivery so we can remove from the next list
                current_node = manager.IndexToNode(index)
                for request in data['pickups_deliveries']:
                    #if we land on dropoff node and have previously been to pickup node
                    if (request[1] == current_node) and (request[0] in self.route_node_list):
                        self.pickups_deliveries_completed.append(request)


                #iterate to next node        
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                #arccost is the distance in this case
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)


            #finish off the ending node
            #we don't need this because it's the dummy node
            '''
            route_node_list.append(manager.IndexToNode(index))
            route_load_list.append(route_load)
            '''

            self.total_distance_each_route_list.append(route_distance)
    
            self.total_distance += route_distance
            self.total_load+= route_load

            self.route_list.append(self.route_node_list)
            self.load_list.append(self.route_load_list)
    def make_json(self):
        self.json_dict = {"route_list": self.route_list, 
                        "load_list": self.load_list, 
                        "distance_list": self.total_distance_each_route_list,
                        "total_distance": self.total_distance,
                        "dropped_nodes": self.dropped_nodes_list,
                        "finished_deliveries": self.pickups_deliveries_completed,
                        "unfinished_deliveries": self.pickups_deliveries_list_unfinished,
                        "untouched_deliveries": self.pickups_deliveries_list_not_started,
                        "false_deliveries": self.pickups_deliveries_list_false_delivery,
                        }
    def print_solution(self):
        print("\n##########################")
        #display route info
        i=0
        for route in self.route_list:
            print(f"Route for vehicle {i+1}:", route)
            print("Load of route:", self.load_list[i])
            print("Total distance of route:", self.total_distance_each_route_list[i])
            i+=1
        
        print("Total distance of all routes", self.total_distance)

        #display dropped nodes
        print("Dropped nodes:", self.dropped_nodes_list)

        #display delivery info
        print("Finished Deliveries:", self.pickups_deliveries_completed)
        print("Unfinished (in progress) Deliveries:", self.pickups_deliveries_list_unfinished)
        print("Not started yet Deliveries:", self.pickups_deliveries_list_not_started)
        print("False Dropoff Deliveries:", self.pickups_deliveries_list_false_delivery)



    
                   


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    # Display dropped nodes.
    dropped_nodes = 'Dropped nodes:'
    dropped_nodes_list = []
    
    #checks for dropped nodes
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if solution.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}'.format(manager.IndexToNode(node))
            dropped_nodes_list.append(manager.IndexToNode(node))
            #prints pickup_delivery pair data for the dropped node
            for request in data['pickups_deliveries']:
                #if node dropped is a dropoff location
                if request[1] == manager.IndexToNode(node):
                    dropped_nodes += '(Delivery node from {0} Load({1}))'.format(request[0], 
                    request[2])
                #if node dropped is a pickup location
                if request[0] == manager.IndexToNode(node):
                    dropped_nodes += '(Delivery to {0} Load({1}))'.format(request[1], 
                    request[2])
                   

    print(dropped_nodes)


    #Display routes
    total_distance = 0
   
    total_load = 0


    delivery_text = 'Finished deliveries:'
    delivery_text_not_started = 'Deliveries not started:'

   
    delivery_text_in_progress = 'Deliveries in progress:'
   



    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    delivery_dimension = routing.GetDimensionOrDie('Delivery')

    #calculate routes for each vehicle
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id+1)
        route_distance = 0
       
        route_load = 0

        #checks until we hit the end of the route
        while not routing.IsEnd(index):

            route_load += data['demands'][manager.IndexToNode(index)]

            plan_output += ' {0} Load({1}) -> '.format(manager.IndexToNode(index), route_load)

            #check if we completed a delivery so we can remove from the next list
            current_node = manager.IndexToNode(index)
            for request in data['pickups_deliveries']:
                #if we land on the delivery node
                if request[1] == current_node:
                    #check if we already visited the pickup node 
                    #this always happens unless we drop the pickup node
                    if (request[0] not in dropped_nodes_list):
                        delivery_text += ' {}'.format(request)
                
                #check if we are on a pickup/dropoff node
                if request[0] == current_node or request[1] == current_node:
                    #when pickup node is dropped it is not started
                    if request[0] in dropped_nodes_list:
                        delivery_text_not_started += ' {}'.format(request)

                    
                    #otherwise when dropoff node is dropped it is in progress
                    elif request[1] in dropped_nodes_list:
                        delivery_text_in_progress += ' {}'.format(request)
                    

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            #arccost is the distance in this case
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)



        plan_output += '{0} Load({1})\n'.format(manager.IndexToNode(index), route_load)
        

        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
   
        plan_output += 'Load of the route: {}\n'.format(route_load)
   
        print(plan_output)
        total_distance += route_distance
   
        total_load+= route_load

    print('Total Distance of all routes: {}m'.format(total_distance))

    print('Total load of all routes: {}'.format(total_load))

    #output delivery status
    print(delivery_text)
    print(delivery_text_in_progress)
    print(delivery_text_not_started)
 

#main(MAX_TRAVEL_DIST, PENALTY, TIME_LIMIT)
def solve(loc_coord_list, plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress):
    """Entry point of the program."""
    # Instantiate the data problem.
    #testing
    #data = create_data_model_sample()

    #use this for actual
    data = create_data_model(loc_coord_list, plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['starts'], data['ends']) 
                                           #data['starts'], data['ends'] or data['depot']

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance   #can use this to constrain power/resources, etc.
        True,  # start cumul to zero
        dimension_name)
    '''#allow dropping nodes'''
    #the penalty for dropping a node (needs to be larger than total path length)
    PENALTY_CONST = 100000
    for node in range(1, len(data['distance_matrix'])):

        '''
        #make in progress deliveries not droppable
        for pickup_ip in data['current_pickups_deliveries']:
            if node == pickup_ip[1]:
                #max int64 value prevents dropping location (solver can't overflow it)
                penalty = 0x7FFFFFFFFFFFFFF
                break
            else:
                #normal penalty needs to be bigger than the total path length
                penalty = PENALTY_CONST
        '''
        
        '''optional makes it more strict (prevents dropping pickup/deliveries)
         maybe have a parameter to enable/disable'''
        #doesn't allow any dropping of pickups_deliveries nodes
        for pickup in data['pickups_deliveries']:
            if node == pickup[1]:
                #max int64 value prevents dropping location (solver can't overflow it)
                #only drops if there is no solution otherwise
                penalty = 0x7FFFFFFFFFFFFFF
                break
            else:
                #normal penalty needs to be bigger than the total path length
                penalty = PENALTY_CONST
        #add the penalty (for dropping) to each node
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
        

    
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)



    ''' WIP, doesn't actually do anything right now
    
        this new capacity method with 2 dimensions should allow separation of pickup and delivery
        so it's easier to do in progress deliveries
        from
        https://gist.github.com/Mizux/5617f65a7be19449fa475cf04b45e50a#file-abhik-py-L282-L289



        PROBLEM: we can't do dropping nodes with this method, otherwise it will mess up the capacity
        so i'm planning on making the solver run again after removing the request
        :(

    '''

    #tracks deliveries (load/unload)
    def delivery_callback(from_index):
        #convert routing variable index to demands node index
        from_node = manager.IndexToNode(from_index)
        return data['delivery_demands'][from_node]


    delivery_callback_index = routing.RegisterUnaryTransitCallback(delivery_callback)

    #define delivery constraint
    routing.AddDimensionWithVehicleCapacity(
        delivery_callback_index,
        0, #null capacity slack
        data['vehicle_capacities'], #vehicle max capacities
        False, #start cumulative variables at zero
        'Delivery' #name
        )



    #net demand of each node
    def demand_callback(from_index):
        #convert routing variable index to demands node index
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]


    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    #define demand constraint
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0, #null capacity slack
        data['vehicle_capacities'], #vehicle max capacities
        False, #start cumulative variables at zero  #this used to be True in the original version
        'Capacity' #name
        )
    
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    delivery_dimension = routing.GetDimensionOrDie('Delivery')
    
    #adds constraint that both dimensions start with same value
    for i in range(data['num_vehicles']):
        index = routing.Start(i)
        #capacity_dimension.SetCumulVarSoftLowerBound(
        #    index=i,
        #    lower_bound=data['vehicle_capacities'][i],
        #    coefficient=100_000_000)
        routing.solver().Add(
            delivery_dimension.CumulVar(index) == capacity_dimension.CumulVar(index))



    #not actually sure what this does lol
    end_index = routing.End(i)
    routing.AddVariableMinimizedByFinalizer(
        delivery_dimension.CumulVar(end_index))
    routing.AddVariableMinimizedByFinalizer(
        capacity_dimension.CumulVar(end_index))
    # capacity_dimension.SetGlobalSpanCostCoefficient(max(data['vehicle_capacities']))






    # Define Transportation Requests.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])


        #routing.AddPickupAndDelivery(pickup_index, delivery_index)
        #routing.solver().Add(
        #     routing.VehicleVar(pickup_index) == routing.VehicleVar(
        #     delivery_index))

        '''acts as a replacement for addpickupanddelivery
            forces a vehicle to go to a specific set of nodes
            doesn't hang the solver when no solution :)
        '''
        #need to check if both nodes are active in the solution
        constraintActive = routing.ActiveVar(pickup_index) * routing.ActiveVar(delivery_index)
        routing.solver().Add(
            constraintActive * routing.VehicleVar(pickup_index) == 
            constraintActive * routing.VehicleVar(delivery_index) )
        ''''''
        #make sure pickup is before delivery
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))

    #in progress deliveries --> make sure we visit the current dropoff node first 
    # (maybe we can make this less strict or something)
    for request in data['current_pickups_deliveries']:
        #pickup index is actually the index of the plane starting node
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        
        #make constraint that we visit delivery node first

        #need to check if both nodes are active in the solution
        constraintActive = routing.ActiveVar(pickup_index) * routing.ActiveVar(delivery_index)
        routing.solver().Add(
            constraintActive * routing.VehicleVar(pickup_index) == 
            constraintActive * routing.VehicleVar(delivery_index) )



    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
   
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

    #time limit needed so that it doesn't try to calculate forever
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution: #sometimes there is no solution or it can't calculate one fast enough
        print_solution(data, manager, routing, solution)
        

        RS = RouteSolution()
        RS.get_solution(data, manager, routing, solution)


        RS.print_solution()


        RS.make_json()
        return RS.json_dict
    else: 
        return None

if __name__ == '__main__':
    #example data
    loc_coord_list = [(1,2), (2, 3), (3, 5)]
    plane_coord_list = [(0, 0), (4, 3), (2, 1)]
    pickups_deliveries = [(4, 5, 1), (6, 4, 3)]
    pickups_deliveries_in_progress = [(6, 5, 1)]

    print(solve(loc_coord_list, plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress))