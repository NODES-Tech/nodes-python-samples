__author__ = 'sre'
import json
from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
session=NodesSession(Environment.DevTest, CLIENT_ID, CLIENT_SECRET)

# Query Trades
result = session.getHandle().get(session.getBaseUrl() + "/Trades", headers=session.getHeader())
for trade in result.json()['items']:
    tradeObj={}
    tradeObj['dealId']=trade['dealId']
    tradeObj['price']=trade['unitPrice']
    tradeObj['buyOrSell']=trade['side']
    tradeObj['quantity']=trade['quantity']
    tradeObj['period']=[trade['periodFrom'],trade['periodTo']]

    #Extract market object
    mres = session.getHandle().get(session.getBaseUrl()  + "/markets/" + trade['marketId'], headers=session.getHeader())
    tradeObj['marketName']=mres.json()['name']

    for link in trade['links']:
        if link['title']=="AssetPortfolio":
            result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
            tradeObj['portfolio']=result2.json()['name']
        if link['title']=="OwnerOrganization":
            result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
            tradeObj['customer']=result2.json()['name']
        if link['title']=="CreatedByUser":
            result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
            tradeObj['user']=result2.json()['links'][0]['title']

    print json.dumps(tradeObj, indent=2)