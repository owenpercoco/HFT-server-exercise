import json, os, socket, sys
from datetime import datetime
	
import numpy as np
from klein import Klein # This is just a thin wrapper over twisted, you can find it here https://github.com/twisted/klein
from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.python import log
high = {"price":0}
last = {}
def now():
    '''
    Return a pretty formatted string of the current datetime

    Returns
    -------
    str : The current time
    '''
    current = datetime.now()
    return current.strftime('%Y-%m-%dT%H:%M:%S.%f')
def get_high():
	global high
	return high
def get_last():
    global last
    return last
def quote_gen():
    ''' 
    Simulate a series of price quotations, periodically emitting a price correction
    a price correction is a quotation whose timestamp is in the past

    Yields
    -------
    dict : the a current or corrected price quotation, with fields 
        {symbol, price, size, timestamp}
    '''
    # Seed the fake price stream
    # and create a variable for price corrections
    price = 250
    correction = None
    global high
    global last
    while True:
        price += np.random.normal(0, 1)
        size = np.round(np.random.exponential(1000), decimals=0)
        record = { "symbol": "AAPL", "price": price, "size": size, "timestamp": now() }
        if record['price'] > get_high()['price']:
			high = record
        last = record
        # Preserve this record as to simulate a correction msg later
        if not correction: correction = record

        # Periodically emit a price correction
        if np.random.binomial(1, .2):
            
            # Modify the price field
            correction['price'] += np.random.normal(0, 1, 1)[0]

            yield correction
            correction = record

        yield record


class QuotationServer(object):
    app = Klein()
    quotes = quote_gen()

    def __init__(self, host, port):
        '''
        Start a server listening at host and port
        with a single route that serves price quotations

        Parameters
        --------
        host (str) : The IP address of the server
        port (str) : The port to bind the tcp endpoint
        '''
        print(host)
        print(port)
        # Configure the http endpoint
        http_endpoint  = endpoints.serverFromString(
            reactor,"tcp:port={port}:interface={host}".format(
                host = host,
                port = port
            )
        )
        
        # Initialize the server
        site = Site(self.app.resource())
        http_endpoint.listen(site)
        log.startLogging(sys.stdout)

        # Kick off the event loop
        reactor.run()

    
    @app.route('/quote')
    def price_quotation(self, request):
        return json.dumps(next(self.quotes))

    @app.route('/high')
    def highest_price(self, request):
        print(get_high())
        return json.dumps(get_high())
    @app.route('/last')
    def last_price(self, request):
        print(get_last())
        return json.dumps(get_last()) 
# Run the server
if __name__ == '__main__':
	print(socket.gethostname())
	print('spinning up server')
	#192.168.0.135
	server = QuotationServer('192.168.0.137', 8585)
