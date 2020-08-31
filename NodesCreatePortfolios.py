import json, string
from NodesApiObjects import nodesAssetTypes, NodesAsset, NodesConnectedAsset, NodesAssetPortfolio, NodesAssetPortfolioAssignment
from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
session=NodesSession(Environment.ExtTest, CLIENT_ID, CLIENT_SECRET)

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

def lookupAssetNameAndId(href):  #lookup from AssetGridAssignment->Asset link
    result = session.getHandle().get(session.getBaseUrl() + href, headers=session.getHeader())
    return result.json()['id'],result.json()['name']

def lookupPolygon(href):  #lookup from GridNode->MapPolygon link
    result = session.getHandle().get(session.getBaseUrl() + href, headers=session.getHeader())
    return result.json()['coordinates']

def lookupGridNodeNameAndId(href):
    polygon=[]  #Also attaching polygon to result. Might be empty if DSO has not registered one for a GridNode
    result = session.getHandle().get(session.getBaseUrl() + href, headers=session.getHeader())
    for link in result.json()['links']:
        if link['title'] == "MapPolygon":
            polygon=lookupPolygon(link['href'])
    return result.json()['id'],result.json()['name'], polygon




result = session.getHandle().get(session.getBaseUrl() + "/users/current", headers=session.getHeader())
myUserId = result.json()['id']

myOrgId=locateCompanyOfUser(myUserId)
dsoOrgId=locateDsoIdFromGridArea("Agder Energi Nett")   #The Grid Area shown in portal

def lookupPortfolioWithName(name):
    result = session.getHandle().get(session.getBaseUrl() + "/assetportfolios", headers=session.getHeader())
    for portfolio in result.json()['items']:
        if portfolio['managedByOrganizationId'] != myOrgId:
            continue
        if portfolio['name']==name:
            return portfolio['id']
    return None


# Query Asset Grid Assigments which is your set of assets that the DSO has approved and assigned to GridNodes
result = session.getHandle().get(session.getBaseUrl() + "/assetgridassignments", headers=session.getHeader())
gnodeMap={}
assetsAssignedMap={}  # just for information, printing Asset name in relation to assignment to grid
for assetassignments in result.json()['items']:
    if assetassignments['managedByOrganizationId']!=myOrgId:
        continue
    if assetassignments['status']== "Pending":  #Exclude assets that have not yet been approved and assigned to grid
        continue
    for link in assetassignments['links']:
        if link['title'] == "GridNode":
            gnodeId, gnodeName, polygon=lookupGridNodeNameAndId(link['href'])
        if link['title'] == "Asset":
            assetId, assetName=lookupAssetNameAndId(link['href'])

    assetsAssignedMap[assetassignments['id']]=assetName
    try:
        gnode=gnodeMap[gnodeId]
        gnode['assets'].append({'id': assetId,'assetGridAssignmentId':assetassignments['id'],  'name': assetName})
    except:
        gnodeMap[gnodeId]={'name':gnodeName, 'polygon': polygon, 'assets':[]}
        gnodeMap[gnodeId]['assets'].append({'id':assetId, 'assetGridAssignmentId':assetassignments['id'], 'name':assetName})


print "Unique GridNodes where participant has assigined assets:"
for key in gnodeMap.keys():
    print gnodeMap[key]['name']
    for asset in gnodeMap[key]['assets']:
        print "\t - " + asset['name']



print "Create portfolio for each gridnode"
# You may want to delete existing portfolios before (re)creating against the current grid assigments or
# check if existing ones actually are unchanged

currentPortfolios={}
result = session.getHandle().get(session.getBaseUrl() + "/assetportfolios", headers=session.getHeader())
for portfolio in result.json()['items']:
    if portfolio['managedByOrganizationId']!=myOrgId:
        continue
    currentPortfolios[portfolio['id']]=portfolio['name']
    #print  json.dumps(portfolio, indent=2)


removePortfolioAllocations=[]
result = session.getHandle().get(session.getBaseUrl() + "/assetportfolioassignments", headers=session.getHeader())
for portcollection in result.json()['items']:
    #print json.dumps(portcollection, indent=2)
    try:
        portname=currentPortfolios[portcollection['assetPortfolioId']]
    except:
        continue
    print "Will remove association between Portfolio:", portname, " and Asset:", assetsAssignedMap[portcollection['assetGridAssignmentId']]
    removePortfolioAllocations.append(portcollection['id'])


#In this sample performing a full cleanup...   in reality check if portfolio exists for a grid node collection of assets
# and consider just to update the assetportfolioassignments mappings to latest assets
#Remove existing associations between portfolios and assetgridassignments (assets)
for toberemoved in removePortfolioAllocations:
    result=session.getHandle().delete(session.getBaseUrl() + "/assetportfolioassignments/" + toberemoved, headers=session.getPostHeader())
    #print "Removal status " , result


for key in currentPortfolios.keys():
    portName=currentPortfolios[key]
    print "Removing portfolio ", portName, "with id ", key
    result=session.getHandle().delete(session.getBaseUrl() + "/assetportfolios/" + key, headers=session.getPostHeader())
    #print  json.dumps(result.json(), indent=2)
    #This will fail if there are orders/baselines connected to this portfolio

exit()
# Create one portfolio for every Grid Node where we have assets, and add these assets to portfolio
for key in gnodeMap.keys():
    gridNodeName= gnodeMap[key]['name']
    print "Create portfolio for grid node:", gridNodeName
    newPortfolioName="Autogen Portfolio " + gridNodeName
    assPortfolio=NodesAssetPortfolio(newPortfolioName)
    assPortfolio.managedByOrganizationId=myOrgId
    assPortfolio.createdByUserId = myUserId
    assPortfolio.lastModifiedByUserId = myUserId
    jsonStr = json.dumps(assPortfolio.__dict__, indent=2)
    result = session.getHandle().post(session.getBaseUrl() + "/assetportfolios", headers=session.getPostHeader(),
                                      data=jsonStr.encode('utf-8'))
    newlyCreatedPortfolioId=lookupPortfolioWithName(newPortfolioName)

    print "New Portfolio ", newPortfolioName, " constructed with ID ", newlyCreatedPortfolioId
    print "\t Polgyon at GridNode associated with this Portfolio ", gnodeMap[key]['polygon']

    for asset in gnodeMap[key]['assets']:  # Loop through all assets under grid node and add to the new portfolio
        assetPortfolioAssginment=NodesAssetPortfolioAssignment(newlyCreatedPortfolioId, asset['assetGridAssignmentId'])
        assetPortfolioAssginment.createdByUserId = myUserId
        assetPortfolioAssginment.lastModifiedByUserId = myUserId
        jsonStr = json.dumps(assetPortfolioAssginment.__dict__, indent=2)
        result = session.getHandle().post(session.getBaseUrl() + "/assetportfolioassignments", headers=session.getPostHeader(),
                                          data=jsonStr.encode('utf-8'))



