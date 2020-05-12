__author__ = 'sre'
import json
from datetime import datetime, timedelta

from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
session=NodesSession(Environment.DevTest, CLIENT_ID, CLIENT_SECRET)

#Query full depth orderbook of anonymous orders
def queryAnonymousOrders(marketId, gridNodeId):
    #Query order for next day, and Up regulation (inc energy, neduction in consumption)  in this sample
    queryFrom=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    queryTo=(datetime.now()+ timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    oderAggregates = session.getHandle().get(session.getBaseUrl() + '/order-aggregates?periodFrom=' + queryFrom+ '&periodTo='+ queryTo + '&regulationType=Up&gridNodeId=' + gridNodeId + "&marketId=" + marketId, headers=session.getHeader())
    for orderItem in oderAggregates.json():
        if len(orderItem['buyItems']) or len(orderItem['sellItems'])>0:  #Only print if there are actual orders placed
            print json.dumps(orderItem, indent=2)

#Query congested zone (Grid Location) associated with a congested grid node. This holds a separate orderbook
def loadCongestedZone(gridNodeId):
    gloc = session.getHandle().get(session.getBaseUrl() + '/gridlocations?gridNodeId=' + gridNodeId, headers=session.getHeader())
    if len(gloc.json()['items'])>0:
        gridLocObj=gloc.json()['items'][0]
        if gridLocObj['status']<>'Active':
            return
        print "GridLocName: ", gridLocObj['name']
        queryAnonymousOrders(gridLocObj['marketId'],gridLocObj['gridNodeId'])

#Query subtree of grid nodes
def querySubTree(rootNode, allGridNodes):
    loadCongestedZone(rootNode)
    for node in allGridNodes:
        if node['parentId']==rootNode:
            querySubTree(node['id'], allGridNodes)

# Query top level grid nodes
result = session.getHandle().get(session.getBaseUrl() + "/gridnodes/grid", headers=session.getHeader())
querySubTree("59c92d61-d1ff-e911-828b-501ac536dc28", result.json())  #Passing root node ID (or Lookup DSO name and root node)



