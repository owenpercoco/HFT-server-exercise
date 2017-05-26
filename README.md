# Python Quote Server Exercise

The goal of this project is to implement a server with two routes
    - /last
      This route should return a json response containing the most recent price quotation
    - /high
      This route should return a json response containing the highest price quotation from the day

To get price quotations, a server is included called `quote_server.py`, running that file will start a server on your machine IP at port 8585.
Sending a GET request to the servers address at the /quote route will result in a JSON blob shaped like:
    { "timestamp": "2017-05-24T13:19:50.152686", 
      "symbol": "AAPL", 
      "price": 257.86215930543216, 
      "size": 370.0
    }

while the timestamps of quotations are monotonically increasing, periodically a correction will be posted. You will be able to recognize a correction,
because its timestamp will have a timestamp earlier than last price quotation. Your routes for `/high` and `/last` should account for quotation corrections.

This project also ensures that you can reproduce the environment with the needed dependencies for the provided server to run.
 Namely:
     - twisted==16.3.0
     - klein==16.2.0
     - numpy==1.10.0
 (versions are provided from my environment)

