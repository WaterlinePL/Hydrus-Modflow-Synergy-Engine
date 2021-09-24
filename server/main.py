# import datapassing.hydrusModflowPassing as dataPasser
# from datapassing.hydrusModflowPassing import HydrusModflowPassing


# def list_all_pods(api: client.CoreV1Api):
#     print("Listing pods with their IPs:")
#     ret = api.list_pod_for_all_namespaces(watch=False)
#     for i in ret.items:
#         print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

from flaskApp import app

if __name__ == '__main__':
    # run flask app
    app.run(debug=True)

