import json, string
from NodesApiObjects import nodesAssetTypes, NodesAsset, NodesConnectedAsset, NodesSellOrder
from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
from datetime import datetime, timedelta
import pytz
session=NodesSession(Environment.ExtTest, CLIENT_ID, CLIENT_SECRET)

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

def lookupMarketProps(marketId):
    result = session.getHandle().get(session.getBaseUrl() + "/markets", headers=session.getHeader())
    for item in result.json()['items']:
        if item['id']==marketId:
            name= item['name']
            blocksize= item['minimumBlockSizeInSeconds']
            timeZone=item['timeZone']
            return name, blocksize, timeZone
    return "", 0, ""

def lookupMarket(gridNodeId):
    result = session.getHandle().get(session.getBaseUrl() + "/gridlocations", headers=session.getHeader())
    for item in result.json()['items']:
        if item['gridNodeId']==gridNodeId:
            marketId= item['marketId']
            marketName, blockSize, timeZone=lookupMarketProps(marketId)
            return marketId, marketName,blockSize, timeZone
    return "","", "",""

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

def lookupGridNodeNameAndId(href):
    result = session.getHandle().get(session.getBaseUrl() + href, headers=session.getHeader())
    return result.json()['id'],result.json()['name']


result = session.getHandle().get(session.getBaseUrl() + "/assetgridassignments", headers=session.getHeader())

asignedAsset={}
for assetassignments in result.json()['items']:
    if assetassignments['managedByOrganizationId']!=myOrgId:
        continue
    if assetassignments['status']== "Pending":  #Exclude assets that have not yet been approved and assigned to grid
        continue
    for link in assetassignments['links']:
        if link['title'] == "GridNode":
            gnodeId, gnodeName=lookupGridNodeNameAndId(link['href'])
            asignedAsset[assetassignments['id']]={'AssignedAssetId':assetassignments['id'],'GridNodeId': gnodeId,'GridNodeName':gnodeName }

tradablePortfolios={}
result = session.getHandle().get(session.getBaseUrl() + "/assetportfolios", headers=session.getHeader())
for portfolio in result.json()['items']:
    if portfolio['managedByOrganizationId']!=myOrgId:
        continue
    tradablePortfolios[portfolio['id']]={'PortfolioId':portfolio['id'], 'PortfolioName':portfolio['name'],'GridNodeId':'','GridNodeName':'','MarketId':'','MarketName':'','assets':[]}
print tradablePortfolios


gnodeMap={}
result = session.getHandle().get(session.getBaseUrl() + "/assetportfolioassignments", headers=session.getHeader())
for item in result.json()['items']:
    try:
        portfolioObj=tradablePortfolios[item['assetPortfolioId']]
        assetGridAssigned=item['assetGridAssignmentId']
        asset=asignedAsset[assetGridAssigned]
        portfolioObj['assets'] .append(asset)
        portfolioObj['GridNodeName']=asset['GridNodeName']
        portfolioObj['GridNodeId'] = asset['GridNodeId']
        try:
            gnode=gnodeMap[portfolioObj['GridNodeId']]
            gnode['portfolios'].append(portfolioObj)
        except:
            gnodeMap[portfolioObj['GridNodeId']]={'portfolios':[]}
            gnodeMap[portfolioObj['GridNodeId']]['portfolios'].append(portfolioObj)
    except:
        pass #Was not our portfolio



#Lookup markets for the different tradable locations
for key in gnodeMap.keys():
    gnodeObj=gnodeMap[key]
    marketId, marketName,blockSize, timeZone=lookupMarket(key)
    for portfolio in gnodeObj['portfolios']:
        portfolio['MarketId'] = marketId
        portfolio['MarketName'] = marketName
        portfolio['MarketBlockSize'] = blockSize
        portfolio['MarketTimeZone'] = timeZone
        print  marketName, portfolio['MarketTimeZone']
    print gnodeObj

for key in gnodeMap.keys():
    gnodeObj=gnodeMap[key]
    addon=-1
    for portfolio in gnodeObj['portfolios']:
        addon+=1  # just to put the offers from portfolios in step wise prices
        for hour in range(8,20):   #Putting in sell orders for all hours in range
            for price in [300,305,310]:  #Putting in multiple offers at different prices
                print "Selling 0.250MW @ " + str(price+ addon) + "NOK on ", portfolio['PortfolioName'], " in ", portfolio['MarketName']
                curr=datetime.now()    #Buy given hour tomorrow
                start=datetime(curr.year,curr.month, curr.day, hour, 0, 0, 0)  +timedelta(days=3)
                end=start+ timedelta(seconds=portfolio['MarketBlockSize'])   #Set end period= blocksize
                nsell = NodesSellOrder(price+ addon, 0.25, convTimeToUtc(start), convTimeToUtc(end))  # Time must be specified in UTC
                nsell.lastModifiedByUserId=myUserId
                nsell.createdByUserId=myUserId
                nsell.marketId=portfolio['MarketId']
                nsell.gridNodeId=key       # Grid Node is the key of the map beeing looped
                nsell.ownerOrganizationId=myOrgId
                nsell.assetPortfolioId=portfolio['PortfolioId']
                jsonStr = json.dumps(nsell.__dict__, indent=2)
                #print  jsonStr
                result = session.getHandle().post(session.getBaseUrl() + "/orders", headers=session.getPostHeader(),
                                                  data=jsonStr.encode('utf-8'))
                print result  #Expecting 200 / OK

