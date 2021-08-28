import datapassing.hydrusModflowPassing as dataPasser
from hydrus.hydrusDeployer import HydrusDeployer
from modflow.modflowDeployer import ModflowDeployer
from datapassing.hydrusModflowPassing import HydrusModflowPassing
from kubernetes import client, config, watch
from flask import Flask, render_template, request, redirect
from zipfile import ZipFile

import os

app = Flask("App")

# ------------ FLASK ------------

all_posts = [
    {
        'title': "post 1",
        'content': "this is content",
        'author': "Marek Gajecki"
    },
    {
        'title': "post 2",
        'content': "this is also content"
    }
]


# template rendering
@app.route('/')
def home():
    return render_template('index.html')


# parameter passing and method declaration - ONLY GET is allowed by default
@app.route('/home/<string:name>', methods=['GET'])
def hello(name):
    return 'sup ' + name


# template functionality showcase
@app.route('/posts')
def posts():
    return render_template('posts.html', posts=all_posts)


# archive uploading

# this should ultimately go into a config file
app.config["PROJECT_DIR"] = '../workspace'
app.config["ALLOWED_TYPES"] = ["ZIP", "RAR", "7Z"]


def type_allowed(filename):

    # check if there even is an extension
    if '.' not in filename:
        return False

    # check if it's allowed
    extension = filename.rsplit('.', 1)[1]
    return extension.upper() in app.config["ALLOWED_TYPES"]


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    # POST handler
    if request.method == 'POST' and request.files:

        project = request.files['archive-input']  # matches HTML input name

        if type_allowed(project.filename):

            # save, unzip, remove archive
            archive_path = os.path.join(app.config["PROJECT_DIR"], project.filename)
            project.save(archive_path)
            with ZipFile(archive_path, 'r') as archive:
                archive.extractall(app.config["PROJECT_DIR"])
            os.remove(archive_path)
            print("Project uploaded successfully")

        else:
            print("Invalid archive format, must be one of: ", end='')
            print(app.config["ALLOWED_TYPES"])

        return redirect(request.url)

    return render_template('upload.html')


# ------------ END FLASK ------------


def list_all_pods(api: client.CoreV1Api):
    print("Listing pods with their IPs:")
    ret = api.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


if __name__ == '__main__':

    # run flask app
    app.run(debug=True)

    # manage kubernetes
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # count = 10
    # watch = watch.Watch()
    # for event in watch.stream(api_instance.list_namespace, _request_timeout=60):
    #     print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    #     print(client.V1PodStatus().container_statuses)
    #     count -= 1
    #     if not count:
    #         watch.stop()

    hydrus_deployer = HydrusDeployer(api_instance=api_instance, pod_name='hydrus-1d')
    hydrus_pod = hydrus_deployer.run_pod()          # returns V1Pod instance

    hydrus_modflow_passing = HydrusModflowPassing()
    hydrus_modflow_passing.update_rch()

    modflow_deployer = ModflowDeployer(api_instance=api_instance, pod_name='modflow-2005')
    modflow_v1_pod = modflow_deployer.run_pod()      # returns V1Pod instance

    # TODO: wait for pods to finish their job and destroy them
    #  current way to delete pod -> kubectl delete pod modflow-2005

    list_all_pods(api=api_instance)
