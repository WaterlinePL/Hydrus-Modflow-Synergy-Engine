
from flask import Flask, render_template, request, redirect
from zipfile import ZipFile

import os

app = Flask("App")

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


if __name__ == "__main__":
    app.run(debug=True)
