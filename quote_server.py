import json, os, socket, sys
from datetime import datetime
	
import numpy as np
from klein import Klein # This is just a thin wrapper over twisted, you can find it here https://github.com/twisted/klein
from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.python import log
'''I used two global variables to keep track of my high and last return values.  
In another scenario, I'd probably use a database for some actual consistency, 
but I just felt like keeping it simple would be in everyones benefit for this short task'''
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
    return current.strftime('%Y-%m-%d %H:%M:%S.%f')

'''Just a couple simple methods to return the previously stated global variables. '''
def get_high():
	global high
	return high
def get_last():
    global last
    return last
def sameDay(record, high):
    '''
    really simple check, checks if the high record is from the same day as the current, since were only checking the highest record for the day.
    '''
    r_day = (record['timestamp'].split(' ')[0])
    r_day = r_day.split('-')
    if 'timestamp' in high:
    	h_day = (high['timestamp'].split(' ')[0])
        h_day = h_day.split('-')
    else:
        return True
    print(r_day)
    return h_day == r_day
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
        '''Heres the logic, essentially if it encounters a price higher than the previous max, it replaces the previous max.  It does the same with the last, simply saving the last value that isn't a correction, which is the only time we travel backwards in time.  '''
        
	if record['price'] > get_high()['price'] and sameDay(record, get_high()):
            high = record
        #if record is from a new day, we just overwrite high with the new record.
        if not sameDay(record, get_high()):
            high = record
        last = record  #setting last to the most recently created record
        # Preserve this record as to simulate a correction msg later
        if not correction: correction = record

        # Periodically emit a price correction
        if np.random.binomial(1, .2):
            	            
            # Modify the price field
            correction['price'] += np.random.normal(0, 1, 1)[0]
            #we also check if the correction throws off our highest price
        
	    if correction['price'] > get_high()['price'] and sameDay(correction, get_high()): 
                        high = correction           
	    #also checking if it was the high that got corrected
            if correction['timestamp'] == get_high()['timestamp'] and sameDay(correction, get_high()):
                        high = correction
	 		print 'in the high correction jumble' 
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
	#this is having trouble on my VM, so Im using actual IPs.  You can probably just use localhost
	server = QuotationServer('192.168.0.19', 8585)
