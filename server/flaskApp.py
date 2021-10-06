from flask import Flask, render_template, request, redirect, url_for
from zipfile import ZipFile

import os

from AppUtils import AppUtils

util = AppUtils()
util.setup()
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
def start():
    return redirect(request.url+"home")


# parameter passing and method declaration - ONLY GET is allowed by default
@app.route('/home/<string:name>', methods=['GET'])
def hello(name):
    return 'sup ' + name


# template functionality showcase
@app.route('/posts')
def posts():
    return render_template('posts.html', posts=all_posts)


# ------------------- END EXAMPLES -------------------


# ------------------- ROUTES -------------------

@app.route('/upload-modflow', methods=['GET', 'POST'])
def upload_modflow():
    if request.method == 'POST' and request.files:
        return upload_modflow_handler(request)
    else:
        return render_template('uploadModflow.html', model_names=util.loaded_modflow_models)


@app.route('/upload-hydrus', methods=['GET', 'POST'])
def upload_hydrus():
    if request.method == 'POST' and request.files:
        return upload_hydrus_handler(request)
    else:
        return render_template('uploadHydrus.html', model_names=util.loaded_hydrus_models)


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

# ------------------- END ROUTES -------------------


# ------------------- HANDLERS -------------------

def upload_modflow_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'modflow', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_modflow_models = [project_name]

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.workspace_dir, 'modflow', project_name))
            archive.extractall(os.path.join(util.workspace_dir, 'modflow'))
        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-modflow')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_hydrus_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'hydrus', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_hydrus_models.append(project_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.workspace_dir, 'hydrus', project_name))
            archive.extractall(os.path.join(util.workspace_dir, 'hydrus', project_name))

        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-hydrus')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)

# ------------------- END HANDLERS -------------------
