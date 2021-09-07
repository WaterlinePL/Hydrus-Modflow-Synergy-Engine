from flask import Flask, render_template, request, redirect
from zipfile import ZipFile

import os

import constants

app = Flask("App")

# ------------------- EXAMPLES -------------------

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


# ------------------- END EXAMPLES -------------------
# archive uploading

# this should ultimately go into a config file
allowed_types = ["ZIP", "RAR", "7Z"]

project_root = constants.PROJECT_ROOT
workspace_dir = os.path.join(project_root, 'workspace')
print(workspace_dir)
modflow_dir = os.path.join(workspace_dir, 'modflow')
hydrus_dir = os.path.join(workspace_dir, 'hydrus')

loaded_hydrus_models = []  # an array of strings, the names of the loaded hydrus models


# create the necessary folder structure
def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


verify_dir_exists_or_create(workspace_dir)
verify_dir_exists_or_create(modflow_dir)
verify_dir_exists_or_create(hydrus_dir)


def type_allowed(filename):

    # check if there even is an extension
    if '.' not in filename:
        return False

    # check if it's allowed
    extension = filename.rsplit('.', 1)[1]
    return extension.upper() in allowed_types


@app.route('/upload-modflow', methods=['GET', 'POST'])
def upload_modflow():

    # POST handler
    if request.method == 'POST' and request.files:

        project = request.files['archive-input']  # matches HTML input name

        if type_allowed(project.filename):

            # save, unzip, remove archive
            archive_path = os.path.join(workspace_dir, 'modflow', project.filename)
            project.save(archive_path)
            with ZipFile(archive_path, 'r') as archive:
                archive.extractall(os.path.join(workspace_dir, 'modflow'))
            os.remove(archive_path)

            print("Project uploaded successfully")
            return redirect(request.root_url + 'upload-hydrus')

        else:
            print("Invalid archive format, must be one of: ", end='')
            print(allowed_types)
            return redirect(request.url)

    return render_template('uploadModflow.html')


@app.route('/upload-hydrus', methods=['GET', 'POST'])
def upload_hydrus():

    # POST handler
    if request.method == 'POST' and request.files:

        project = request.files['archive-input']  # matches HTML input name

        if type_allowed(project.filename):

            # save, unzip, remove archive
            archive_path = os.path.join(workspace_dir, 'hydrus', project.filename)
            project.save(archive_path)
            with ZipFile(archive_path, 'r') as archive:

                # get the project name and remember it
                project_name = project.filename.split('.')[0]
                loaded_hydrus_models.append(project_name)

                # create a dedicated catalogue and load the project into it
                os.system('mkdir ' + os.path.join(workspace_dir, 'hydrus', project_name))
                archive.extractall(os.path.join(workspace_dir, 'hydrus', project_name))

            os.remove(archive_path)

            print("Project uploaded successfully")
            return redirect(request.root_url + 'upload-hydrus')

        else:
            print("Invalid archive format, must be one of: ", end='')
            print(allowed_types)
            return redirect(request.url)

    return render_template('uploadHydrus.html', model_names=loaded_hydrus_models)
