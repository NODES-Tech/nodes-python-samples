__author__ = 'sre'
import json
from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
session=NodesSession(Environment.DevTest, CLIENT_ID, CLIENT_SECRET)

# Query Markets
result = session.getHandle().get(session.getBaseUrl() + "/markets", headers=session.getHeader())

for market in result.json()['items']:
    if market['name']!= "Example Flex Market ":   #Limit on specific market in this test
        continue
    orderList=[]
    for link in market['links']:  #loop through own orders in this market
        if link['title']=="Orders":
            resList = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
            for order in resList.json()['items']:
                print json.dumps(order, indent=2)
                orderObj={}
                orderObj['orderId']=order['id']
                orderObj['buyOrSell']=order['side']
                orderObj['quantity']=order['quantity']
                orderObj['price']=order['unitPrice']
                orderObj['period']=[order['periodFrom'],order['periodTo']]
                for link in order['links']:
                    if link['title']=="AssetPortfolio":
                        result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
                        orderObj['portfolio']=result2.json()['name']
                    if link['title']=="OwnerOrganization":
                        result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
                        orderObj['customer']=result2.json()['name']
                    if link['title']=="CreatedByUser":
                        result2 = session.getHandle().get(session.getBaseUrl()  + link['href'], headers=session.getHeader())
                        orderObj['user']=result2.json()['links'][0]['title']

                orderList.append(orderObj)  # Adding simplified order object after looking up reference keys


print orderList