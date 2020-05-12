# nodes-python-samples
Python samples on integrating with the NODES REST API.
Dependencies: 
- Python 2.7
- pip install enum34
- pip install rauth


NodesSession.py
URLs and example on using OAuth and Client Id/Secret to authenticate with the NODES platform. 

NodesTradeCollector.py
Authenticated as App client linked to a NODES customer (company), this file extract all recent trade recordes matched in NODES. Use for scheduling Dispatch on assets according to MW (Quantity) and Period (given in UTC from API)

NodesParseGridTopology.py
Script for parsing the DSO's topology of Grid Nodes via Grid Links (with links to congested Nodes given as Grid Locations)

NodesQueryOwnOrders.py
Script for querying own orders active, cancelled, filled in market. Contain all details on orders since they belong to associated customer (company) of app client.

NodesQueryFlexMarket.py
Script for querying the full orderbooks in market under a topology; returning anonymous aggregated orders grouped by price. Provides a snapshot of the market at the point of query. 
