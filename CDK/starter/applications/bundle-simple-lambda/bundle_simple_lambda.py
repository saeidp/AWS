import urllib3
import json

def handler(event,context):
        resp = urllib3.request( method='GET',
                                url="http://asdfast.beobit.net/api/",
                                headers={'Accept': 'application/json'}, timeout=5)
        return {
                "status": resp.status,
                "data": json.loads(resp.data)  

        }
