"""

Basic Tests against the Skyscraper API
VMC API documentation available at https://vmc.vmware.com/swagger/index.html#/
CSP API documentation is available at https://saas.csp.vmware.com/csp/gateway/api-docs
vCenter API documentation is available at https://code.vmware.com/apis/191/vsphere-automation


You can install python 3.6 from https://www.python.org/downloads/windows/

You can install the dependent python packages locally (handy for Lambda) with:
pip install requests -t . --upgrade
pip install configparser -t . --upgrade

"""

import requests                         # need this for Get/Post/Delete
import configparser                     # parsing config file
import time


config = configparser.ConfigParser()
config.read("./config.ini")
strProdURL      = config.get("vmcConfig", "strProdURL")
strCSPProdURL   = config.get("vmcConfig", "strCSPProdURL")
Refresh_Token   = config.get("vmcConfig", "refresh_Token")
ORG_ID          = config.get("vmcConfig", "org_id")
User_Name       = config.get("vmcConfig", "user_name")
Sddc_name		= config.get("vmcConfig", "sddc_name")
Sddc_hosts		= config.get("vmcConfig", "sddc_hosts")
Sddc_provider	= config.get("vmcConfig", "sddc_provider")
Sddc_region		= config.get("vmcConfig", "sddc_region")
Sddc_subnet		= config.get("vmcConfig", "sddc_subnet")
Sddc_aws_acc	= config.get("vmcConfig", "sddc_aws_acc")
Sddc_deploy		= config.get("vmcConfig", "sddc_deploy")
Sddc_mngt		= config.get("vmcConfig", "sddc_mngt")


# To use this script you need to create an OAuth Refresh token for your Org
# You can generate an OAuth Refresh Token using the tool at vmc.vmware.com
# https://console.cloud.vmware.com/csp/gateway/portal/#/user/tokens


class data():
    sddc_name       = ""
    sddc_status     = ""
    sddc_region     = ""
    sddc_cluster    = ""
    sddc_hosts      = 0
    sddc_type       = ""

def getAccessToken(myKey):
    params = {'refresh_token': myKey}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    jsonResponse = response.json()
    access_token = jsonResponse['access_token']
    return access_token

# -------Get SDDC State ---------


def getSDDCstate(sddcID, orgid, sessiontoken):
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + orgid + "/sddcs/" + sddcID
    response = requests.get(myURL, headers=myHeader)
    jsonResponse = response.json()
    data.sddc_name           =   jsonResponse['name']
    data.sddc_state          =   jsonResponse['sddc_state']
    data.sddc_cluster        =   jsonResponse['resource_config']['clusters'][0]['cluster_name']
    data.sddc_type           =   jsonResponse['resource_config']['deployment_type']
    data.sddc_region         =   jsonResponse['resource_config']['region']

    if jsonResponse['resource_config']:
        hosts = jsonResponse['resource_config']['esx_hosts']
    if hosts:
        for j in hosts:
            data.sddc_hosts += 1
    return()


def getSDDC_ID(orgID, session_token):
    myHeader = {'csp-auth-token': session_token}
    myURL = strProdURL + "/vmc/api/orgs/" + orgID + "/sddcs"
    response = requests.get(myURL, headers=myHeader)
    sddc_list = response.json()
    for sddc in sddc_list:
        name = sddc['user_name']
        if name == User_Name:
            return(sddc['id'])
    return"not-found"

def createSDDC(orgid, sessiontoken):

    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + orgid + "/sddcs"
    strRequest = {
        "num_hosts": Sddc_hosts,
        "name": Sddc_name,
        "provider": Sddc_provider,
        "region": Sddc_region,
        "account_link_sddc_config":
            [
                {
                    "customer_subnet_ids": [Sddc_subnet],
                    "connected_account_id": Sddc_aws_acc
                }
            ],
        "sddc_type": "",
        "deployment_type": Sddc_deploy,
        "vxlan_subnet": Sddc_mngt
    }

    response = requests.post(myURL, json=strRequest, headers=myHeader)
    jsonResponse = response.json()

    if str(response.status_code) != "202":
        print("\nERROR: " + str(jsonResponse['error_messages'][0]))

    return
# --------------------------------------------
# ---------------- Main ----------------------
# --------------------------------------------


session_token = getAccessToken(Refresh_Token)


sddcID = getSDDC_ID(ORG_ID, session_token)
if sddcID == "not-found":
    print("SDDC not found....Creating new SDDC")
    createSDDC(ORG_ID, session_token)
    time.sleep(120)


sddcID = getSDDC_ID(ORG_ID, session_token)
print("\n")
print("SDDC ID........... " + sddcID)


getSDDCstate(sddcID, ORG_ID, session_token)
print("SDDC Name......... " + data.sddc_name)
print("SDDC Cluster...... " + data.sddc_cluster)
print("Number of Hosts .. " + str(data.sddc_hosts))
print("Deployed in ...... " + data.sddc_type)
print("AWS Region........ " + data.sddc_region)
print("\n")





