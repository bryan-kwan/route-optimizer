#assumes 2D motion 
#have to change calculations for 3D motion (prob not too hard)


import math

#used append for generate_distance_matrix() so there's a chance
#for things to go terribly wrong if we feed it bad data, etc.


#takes the plane coordinate list and location coordinate list
#and outputs the distance matrix
#format of our distance_matrix is
#[
# [dummy node distance row (all 0)],
# [plane node distances],
# ...
#  
# [location node distances],
# ...

# ]

#high value constant so that planes are ideally infinite distance apart
PLANE_DIST_CONST = 10000000

def generate_distance_matrix(loc_coord_list, plane_coord_list):
    distance_matrix = []

    #calculate the size we need for our matrix
    #we always have 1 dummy depot node
    matrix_size = 1
    matrix_size += len(plane_coord_list)
    matrix_size += len(loc_coord_list)

    #the first row is the dummy node and filled with 0s
    dummy_row = [0 for i in range(matrix_size)]

    #add to the matrix
    distance_matrix.append(dummy_row)

    #calculate distance between 2D points
    def calculate_distance(coord1, coord2):
        x0 = coord1[0]
        y0 = coord1[1]
        x1 = coord2[0]
        y1 = coord2[1]
        distance = math.sqrt((x0-x1)**2 + (y0-y1)**2)
        return distance

    #iterate through each plane coordinate to find the distance to every location coordinate
    for plane_coord in plane_coord_list:
        row = []

        #the first entry in each row of the distance matrix is the distance to
        # the dummy depot which has distance 0 from every other node
        row.append(0)

        #we don't actually need the distances to the other planes but maybe it's nice to know
        for temp_coord in plane_coord_list:
            distance = calculate_distance(temp_coord, plane_coord)
            row.append(distance)
        
        #add implementation for very large distances between planes here
        '''

        ///

        '''

        #fill the row with distances to each other coord
        for loc_coord in loc_coord_list:
            distance = calculate_distance(plane_coord, loc_coord)
            row.append(distance)
        
        #add the row to the distance_matrix
        distance_matrix.append(row)


    #iterate through each location coordinate to find the distance to every other location coordinate
    for loc_coord in loc_coord_list:
        row = []

        #the first entry in each row of the distance matrix is the distance to
        # the dummy depot which has distance 0 from every other node
        row.append(0)

        #distance to each plane
        for temp_coord in plane_coord_list:
            distance = calculate_distance(temp_coord, loc_coord)
            row.append(distance)
        

        #fill the row with distances to each other coord
        for loc_coord_2 in loc_coord_list:
            distance = calculate_distance(loc_coord, loc_coord_2)
            row.append(distance)
        
        #add the row to the distance_matrix
        distance_matrix.append(row)

        
    return distance_matrix


#expects the lists with triplets of the form
#[(pickup node, delivery node, number of people),...]
#also needs total number of nodes (dummy, planes, locations)

#outputs [pickup_demand, delivery_demand] at each node (we make pickup positive and delivery negative)
def generate_demand(pickups_deliveries_requests, pickups_deliveries_requests_in_progress, number_nodes):

    pickup_demand = [0 for i in range(number_nodes)]
    delivery_demand = [0 for i in range(number_nodes)]

    #demand at out dummy node will always be 0
    #reassigning for safety
    pickup_demand[0] = 0
    delivery_demand[0] = 0
    pickup_demand_in_prog = pickup_demand.copy()
    delivery_demand_in_prog = pickup_demand.copy()


    #can define demand for in progress pickup_deliveries by assigning a demand to our 
    # starting (plane position) node
    #then we put the negative demand on our delivery node
    #and in the solver force the plane to go to that node first or prioritize it, or not allow dropping, etc.
    for pickup_delivery_in_prog in pickups_deliveries_requests_in_progress:
        #pickup node will be a plane node
        pickup_node = pickup_delivery_in_prog[0]
        delivery_node = pickup_delivery_in_prog[1]
        load_node = pickup_delivery_in_prog[2]
        
        #pickup positive delivery negative demand
        pickup_demand_in_prog[pickup_node] = load_node
        delivery_demand_in_prog[delivery_node] = -load_node

    #demand at each location node
    for pickup_delivery in pickups_deliveries_requests:
        pickup_node = pickup_delivery[0]
        delivery_node = pickup_delivery[1]
        load_node = pickup_delivery[2]
        
        #pickup positive delivery negative demand
        pickup_demand[pickup_node] = load_node
        delivery_demand[delivery_node] = -load_node

    

    return [pickup_demand, delivery_demand, pickup_demand_in_prog, delivery_demand_in_prog]








#when the solver drops a node, it always
# drops a request before it starts
#this happens when it can't 
#find a solution so we need to run it again with the proper
#demand setup by dropping that request's demand


#it also can't drop a request in progress


#generates demand when we drop a node
def generate_dropped_demand(pickups_deliveries_requests, 
                            pickups_deliveries_requests_in_progress, 
                            number_nodes, 
                            dropped_requests):
    #use this method to calculate the route when we drop a list of requests

    #we can just use generate_demand() but we need to 
    # remove the dropped node's demand first
    for d_request in dropped_requests:
        #only need to take care of the to_do requests because only these get dropped
        for request in pickups_deliveries_requests:
            #checks which request is the request we dropped
            if d_request == request:
                #temporarily remove it from the requests to run the solver again
                pickups_deliveries_requests.remove(request)
    
    #generate demand after removing the dropped request
    demand_data = generate_demand(pickups_deliveries_requests, 
        pickups_deliveries_requests_in_progress, number_nodes)

    return demand_data



if __name__ == "__main__":
    loc_coord_list = [(1,2), (2, 3), (3, 5)]
    plane_coord_list = [(0, 0), (4, 3), (2, 1)]
    print(generate_distance_matrix(loc_coord_list, plane_coord_list))

    pickups_deliveries_requests = [(4, 5, 1), (6, 4, 3)]
    pickups_deliveries_requests_in_progress = [(6, 5, 1)]
    matrix_size = len(generate_distance_matrix(loc_coord_list, plane_coord_list)[0])
    print(generate_demand(pickups_deliveries_requests, pickups_deliveries_requests_in_progress, matrix_size))

    dropped_list = [pickups_deliveries_requests[0]]
    print(generate_dropped_demand(pickups_deliveries_requests, 
        pickups_deliveries_requests_in_progress, matrix_size, dropped_list ))

