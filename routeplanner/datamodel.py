#modified from https://developers.google.com/optimization/routing
from generatedata import generate_demand, generate_distance_matrix

#input: list of location coordinates, list of plane coordinates, pickup/delivery requests (and in progress ones)
def create_data_model(loc_coord_list, plane_coord_list, pickups_deliveries, pickups_deliveries_in_progress):
    """Stores the data for the problem."""
    data = {}
    
    #lets make this model store the same things as the database to make it easy
    data['loc_coord_list'] = loc_coord_list
    data['plane_coord_list'] = plane_coord_list
    


    #distance to each other node 
    #eg. [0][1] is the distance from node 0 to node 1

    #set distance from the depot (index 0) to every other point to be 0
    #so that we can have different start/stop locations
    data['distance_matrix'] = generate_distance_matrix(loc_coord_list, plane_coord_list)
    

    #[pickup node index, destination node index, load]
    #there is a problem with AddPickupAndDelivery() where the solver may hang if there is no solution
    data['pickups_deliveries'] = pickups_deliveries
    
    #keep track of pickup_deliveries in progress if we calculate mid-route
    data['current_pickups_deliveries'] = pickups_deliveries_in_progress
    
    data['num_vehicles'] = len(plane_coord_list)

    #where all the vehicles return to from each route
    data['depot'] = 0

    #we need to add a capacity constraint
    number_nodes = len(data['distance_matrix'][0])
    demand_data = generate_demand(pickups_deliveries, pickups_deliveries_in_progress, number_nodes)
    data['pickup_demands'] = demand_data[0]
    data['delivery_demands'] = demand_data[1]
    data['current_pickup_demands'] = demand_data[2]
    data['current_delivery_demands'] = demand_data[3]
    #net pickups_deliveries demand
    data['demands'] = []
    for (item1, item2) in zip(data['pickup_demands'],data['delivery_demands']):
        data['demands'].append(item1 + item2)
    #net in progress demand
    data['current_demands'] = []
    for (item1, item2) in zip(data['current_pickup_demands'],data['current_delivery_demands']):
        data['current_demands'].append(item1 + item2)
    #add demand of in progress pickups_deliveries 
    temp = []
    for (item1, item2) in zip(data['demands'] ,data['current_demands']):
        temp.append(item1 + item2)
    data['demands'] = temp.copy()

    #just going to assume these will be constant and that we don't need to input
    CAPACITY_CONST = 15
    data['vehicle_capacities'] = [CAPACITY_CONST for i in range(data['num_vehicles'])]

    #start/stop locations are the plane current locations
    #plane 1 is node 1, plane 2 is node 2, etc.
    data['starts'] = [(i+1) for i in range(data['num_vehicles'])]
    #end on the dummy depot node
    data['ends'] = [0 for i in range(data['num_vehicles'])]


    '''not used currently'''
    #max node index so we can ignore the dummy (the dummy index is 0 and everything > the last node)
    data['max_index'] = number_nodes-1


    return data


def create_data_model_sample():
    """Stores the data for the problem."""
    data = {}
    #distance to each other node 
    #eg. [0][1] is the distance from node 0 to node 1

    #set distance from the depot (index 0) to every other point to be 0
    #so that we can have different start/stop locations
    data['distance_matrix'] = [
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            0, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            0, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            0, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            0, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            0, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            0, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            0, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            0, 1084, 514
        ],
        [
            0, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            0, 810, 468
        ],
        [
            0, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            0, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            0, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            0, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            0, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            0, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            0, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    
    ]
    

    #[pickup node index, destination node index, load]
    #there is a problem with AddPickupAndDelivery() where the solver may hang if there is no solution
    data['pickups_deliveries'] = [
        
        # [2, 10, 10],
        # [10,3, 3], 
        # #[10,6,0], #causes problems for the addpickupandelivery method
        # [6,3, 0],
        # [7, 9, 6],
        # [15,16, 4],
        # [13,14,1],
        # [11,12,5],
        # [4,5,2],
        # [5,8,0],
        
        [5, 6, 1],
        [6, 8, 2],
        [7, 10, 3],
        #test PROBLEM
        #[15,7,5],
    ]
    
    #keep track of pickup_deliveries in progress if we calculate mid-route
    data['current_pickups_deliveries'] = [
        [1, 16, 1],
    ]
    
    data['num_vehicles'] = 4
    #where all the vehicles return to from each route
    data['depot'] = 0

    #we need to add a capacity constraint
    #data['demands'] = [0, 0, 10, -3, 2, -2, 0, 6, 0, -6, -7, 5, -5, 1, -1, 4, -4]
    
    data['pickup_demands'] = [0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    data['delivery_demands'] = [0,0,0,0,0,0,-1,0,-2,0,-3,0,0,0,0,0,0]
    data['current_delivery_demands'] = [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1]
    #net demand of pickups_deliveries
    data['demands'] = []
    for (item1, item2) in zip(data['pickup_demands'],data['delivery_demands']):
        data['demands'].append(item1 + item2)
    #add demand of in progress pickups_deliveries 
    temp = []
    for (item1, item2) in zip(data['demands'] ,data['current_delivery_demands']):
        temp.append(item1 + item2)
    data['demands'] = temp.copy()

    data['vehicle_capacities'] = [15,15,20,15] #[15,15,15,15]
    #start/stop locations
    #note Start index can't be a pickup/dropoff location!!!!!
    data['starts'] = [1,2,3,4]
    #end on the dummy depot node
    data['ends'] = [0,0,0,0]

    #max node index so we can ignore the dummy (the dummy index is 0 and everything > the last node)
    data['max_index'] = len(data['distance_matrix'])-1

    return data



if __name__ == "__main__":
    loc_coord_list = [(1, 2), (2, 3), (3, 4)]
    plane_coord_list = [(0,0), (1, 1), (2,2), (3,3)]
    pickups_deliveries = [(4, 5, 1), (6, 4, 3)]
    pickups_deliveries_in_progress = [(6, 5, 1)]

    data = create_data_model(loc_coord_list, plane_coord_list, 
        pickups_deliveries, pickups_deliveries_in_progress)
    
    print(data)