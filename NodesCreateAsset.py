import json, string
from NodesApiObjects import nodesAssetTypes, NodesAsset, NodesConnectedAsset
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
    # User have memberships that are visualized through company's subscriptions (FSP, BRP etc)
    for memships in result.json()['items']:  # At the moment could have multiple....  future model will simplify with direct link to organization
        subsid = memships['subscriptionId']
        result = session.getHandle().get(session.getBaseUrl() + "/subscriptions/" + subsid,
                                         headers=session.getHeader())
        orgId = result.json()['ownerOrganizationId']
    return orgId

result = session.getHandle().get(session.getBaseUrl() + "/users/current", headers=session.getHeader())
myUserId = result.json()['id']

myOrgId=locateCompanyOfUser(myUserId)                   # This sample assumes that my organization is both BRP and FSP, and this ID is used for both references in assignment of asset
dsoOrgId=locateDsoIdFromGridArea("Agder Energi Nett")   #The Grid Area shown in portal

# Query Asset Types, and store ID in dicstionary
result = session.getHandle().get(session.getBaseUrl() + "/assetTypes", headers=session.getHeader())

#print json.dumps(result.json(), indent=2)
for atype in result.json()['items']:
    nodesAssetTypes[atype['name']]=atype['id']
print "Asset Type IDs ", nodesAssetTypes

# Create the core Asset objected to be stored in NODES
asset=NodesAsset("My weak battery")
asset.assetTypeId=nodesAssetTypes['Battery']  # Assuming battery is found amongs available types
asset.externalReference="AssetHubID5462"     #Could be any ID but should be Unique for your organizationb so you can look up the generated ID from the next registration step
asset.createdByUserId=myUserId
asset.lastModifiedByUserId=myUserId
asset.operatedByOrganizationId=myOrgId
jsonStr = json.dumps(asset.__dict__, indent=2)

# Store asset in NODES; not yet assigning it to a particular DSO
result = session.getHandle().post(session.getBaseUrl() + "/assets", headers=session.getPostHeader(), data=jsonStr.encode('utf-8'))
#print json.dumps(result.json(), indent=2)

# Reload asset to see generated Asset ID which needs to be used in assigning asset to grid of DSO
# Query Asset Types, and store ID in dicstionary
result = session.getHandle().get(session.getBaseUrl() + "/assets", headers=session.getHeader())
newAssetId=""
for assetItem in  result.json()['items']:
    if assetItem['externalReference']==asset.externalReference:
        print "Found newly created asset with ID ", assetItem['id']
        newAssetId=assetItem['id']

# Create the link between the Asset and a particular DSO + MPID
connectedAsset=NodesConnectedAsset(6.92891, 58.2903, newAssetId, asset.externalReference)
connectedAsset.mpid="705011111111331" # The MPID
connectedAsset.managedByOrganizationId=myOrgId  # Assign the ID of the current FSP registering the Asset connection
connectedAsset.suppliedByOrganizationId=myOrgId  # Often our own organization is also BRP on the MPID level
connectedAsset.operatedByOrganizationId=dsoOrgId
connectedAsset.createdByUserId=myUserId
connectedAsset.lastModifiedByUserId=myUserId

jsonStr = json.dumps(connectedAsset.__dict__, indent=2)
# Store asset connection to grid (MPID, Long/Lat and DSO ID in particular
result = session.getHandle().post(session.getBaseUrl() + "/assetgridassignments", headers=session.getPostHeader(), data=jsonStr.encode('utf-8'))

#print result
#print json.dumps(result.json(), indent=2)
