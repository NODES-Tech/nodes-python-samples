__author__ = 'sre'
import json
from NodesSession import NodesSession, Environment
from NodesAuthentication import CLIENT_ID, CLIENT_SECRET
session=NodesSession(Environment.DevTest, CLIENT_ID, CLIENT_SECRET)

#Query full topolgy by following GridNode => (either Grid Location or Grid Links with current node as Source in link)
def gridLinkParser(href):
    result = session.getHandle().get(session.getBaseUrl() + href + "&Take=30", headers=session.getHeader())
    for it in result.json()['items']:
        for link in it['links']:
            if  link['rel']=="gridnode target":
                gridNodeParser(link['href'])

def gridNodeParser(href):
    result = session.getHandle().get(session.getBaseUrl() + href + "&Take=30", headers=session.getHeader())
    node=result.json()
    for link in node['links']:
        if link['rel']=="source gridnodelink":
            gridLinkParser( link['href'])
        if link['rel']==" gridlocation":
            gloc = session.getHandle().get(session.getBaseUrl() + link['href'], headers=session.getHeader())
            if len(gloc.json()['items'])>0:
                if gloc.json()['items'][0]['status']<>'Active':
                    continue
                print "GridLocName: ", gloc.json()['items'][0]['name']


# Query top level grid nodes
result = session.getHandle().get(session.getBaseUrl() + "/gridnodes/grid", headers=session.getHeader())
for gnode in result.json():
    if  gnode['parentId']=="59c92d61-d1ff-e911-828b-501ac536dc28":   #ID of top level NODE (or filter on name)
        if gnode['name'] is not None:
            gridNodeParser( "/gridnodes/" + gnode['id'])



