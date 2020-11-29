document.write("Hello world");
            
//get data from database
function request_data(){
                
}

//calculate optimized route
//we want to send an asynchronous request
function plan_route(){
    //using ajax to do run our python script asynchronously
    $.ajax({
        type: "POST",
        url: "routecalculator.py",
        data: { param: input }, 
        success: call_back_function
    });
}

//display new route and post update to the database
function call_back_function(response){
    //show the data
    //...

    //update our database
    send_data(data)

}

//send new route to database
function send_data(data){
                
}
