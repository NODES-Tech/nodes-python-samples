import json, string
from NodesApiObjects import nodesAssetTypes, NodesAsset, NodesConnectedAsset, NodesBuyOrder
from NodesSession import NodesSession, Environment
from NodesAuthentication import DSO_CLIENT_ID, DSO_CLIENT_SECRET
from datetime import datetime, timedelta
import pytz
session=NodesSession(Environment.ExtTest, DSO_CLIENT_ID, DSO_CLIENT_SECRET)

def convTimeToUtc(input):  #Sample assumes central europe timezone
    tzNorw = pytz.timezone('Europe/Oslo')
    ct = datetime.now(tz=tzNorw)
    local_dt = tzNorw.localize(input, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def locateDsoIdFromGridArea(gridAreaName):
    result = session.getHandle().get(session.getBaseUrl() + "/GridAreas/", headers=session.getHeader())
    for area in result.json()['items']:
        if area['name']==gridAreaName:
            for link in area['links']:
                if link['title']=="OperatedByOrganization":
                    cols=string.split(link['href'], "/")   # Extract the ID part of the href link
                    id=cols[len(cols)-1]
                    return id
    return None

def locateCompanyOfUser(userId):
    orgId=None
    #Lookup memberships
    result = session.getHandle().get(session.getBaseUrl() + "/memberships?userId=" + myUserId,
                                     headers=session.getHeader())
    for memships in result.json()['items']:
        orgId = memships['organizationId']
        #Could be linked to multiple organization. For simplicity select the last one...
    return orgId

result = session.getHandle().get(session.getBaseUrl() + "/users/current", headers=session.getHeader())
myUserId = result.json()['id']

myOrgId=locateCompanyOfUser(myUserId)                   # This sample assumes that my organization is both BRP and FSP, and this ID is used for both references in assignment of asset
dsoOrgId=locateDsoIdFromGridArea("Agder Energi Nett")   #The Grid Area shown in portal



result = session.getHandle().get(session.getBaseUrl() + "/markets?Take=200", headers=session.getHeader())
for market in result.json()['items']:
    if market['ownerOrganizationId']==dsoOrgId and market['quantityType']=="Power":
        marketId=market['id']

gnodeName=""
result = session.getHandle().get(session.getBaseUrl() + "/gridnodes?Take=200", headers=session.getHeader())
for gnode in result.json()['items']:
    #print gnode['name']
    if  gnode['operatedByOrganizationId']==dsoOrgId and  gnode['name']=="Mandal Trafo (IME)":
        gnodeId = gnode['id']
        gnodeName=gnode['name']
#print "Lookup orders at GridNode ", gnodeId, " and Market ", marketId

quantity=5
for hour in range(8,14):   #Putting in buy orders with higher price in certain hours
    if hour==10 or hour==11 or hour==12:
        price=500
    else:
        price=310

    print "Buying 5MW @ " + str(price) + "NOK on GridNode " + str(gnodeName) + " in hour " + str(hour)
    curr=datetime.now()    #Buy given hour tomorrow
    start=datetime(curr.year,curr.month, curr.day, hour, 0, 0, 0)  +timedelta(days=1)
    end = start +timedelta(seconds=3600)  # 1800 if half hour ISPs
    order_json = NodesBuyOrder(price, quantity, convTimeToUtc(start), convTimeToUtc(end))
    order_json.lastModifiedByUserId = myUserId
    order_json.createdByUserId = myUserId
    order_json.marketId = marketId
    order_json.gridNodeId = gnodeId  # Grid Node is the key of the map beeing looped
    order_json.ownerOrganizationId = dsoOrgId
    jsonStr = json.dumps(order_json.__dict__, indent=2)
    #print jsonStr
    result = session.getHandle().post(session.getBaseUrl() + "/orders", headers=session.getPostHeader(),
                                      data=jsonStr.encode('utf-8'))
    #print result  # Expecting 200 / OK
