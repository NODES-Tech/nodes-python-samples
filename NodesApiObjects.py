__author__ = 'steinarruneeriksen'
from datetime import datetime
import json
nodesAssetTypes={

}

class NodesAsset:

    def __init__(self, assetName="AssetName"):
        n=datetime.now()
        self.id = None
        self.name=assetName
        self.comments=""
        self.assetTypeId=""
        self.operatedByOrganizationId=""  #Company of asset owner.
        self.rampUpRate=0
        self.rampDownRate=0
        self.externalReference=""
        self.status="Pending"
        self.created=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.createdByUserId=""
        self.lastModified=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.lastModifiedByUserId=""

class NodesAssetPortfolioAssignment:
    def __init__(self, assetPortfolioId, assetGridAssignmentId):
        n=datetime.now()
        self.id = None
        self.assetPortfolioId=assetPortfolioId
        self.assetGridAssignmentId=assetGridAssignmentId
        self.status="Received"
        self.created=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.createdByUserId=""
        self.lastModified=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.lastModifiedByUserId=""

class NodesAssetPortfolio:

    def __init__(self, assetPortfolioName="Portfolio"):
        n=datetime.now()
        self.id = None
        self.name=assetPortfolioName
        self.comments=""
        self.assetTypeIds=[]
        self.managedByOrganizationId=""  #Company of asset portfolio owner.
        self.renewableType="Mixed"
        self.externalReference=""
        self.status="Active"
        self.created=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.createdByUserId=""
        self.lastModified=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.lastModifiedByUserId=""



class NodesConnectedAsset:

    def __init__(self, longitude=0,latitude=0, assetId="", externRef=""):
        n=datetime.now()
        self.id = None
        self.assetId=assetId
        self.mpid = ""
        self.location = {"longitude":longitude, "latitude":latitude}
        self.gridNodeId=None   #To be set by DSO when approving the asset
        self.subMeterId=""
        self.managedByOrganizationId = ""  # My own FSP ID
        self.operatedByOrganizationId=""   # The DSO where the Asset is being registered
        self.suppliedByOrganizationId = ""  # Current BRP on MPID level. Sometimes the same as my FSP is FSP is also BRP
        self.comments=""
        self.powerContribution=0 # Bug... should be on links in grid rather than asset. Hwo much all assets one one location contributes at level above (0<100%)
        self.externalReference=externRef
        self.status="Pending"
        self.created=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.createdByUserId=""
        self.lastModified=n.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.lastModifiedByUserId=""



if __name__ == "__main__":
    a=NodesAsset()
    jsonStr = json.dumps(a.__dict__)
    print jsonStr


