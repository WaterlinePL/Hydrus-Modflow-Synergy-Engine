// model removal
async function doDelete(modelName) {
    var url = Config.uploadHydrus;
    await fetch(url, {
        method: "DELETE",
        body: JSON.stringify({modelName: modelName})
    }).then(response => {
        if (response.status === 200) {
            location.replace(response.url)
        }
    });
}

(function($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================
    var models = Array.from($('#models-list').children());
    models = models.map(item => item.innerText);


    var dropZone = document.getElementById('drop-zone');

    async function startUpload(files) {
        console.log("HYDRUS");
        const formData = new FormData();
        for (let i = 0; i < files.length; i++)
            formData.append('archive-input', files[i]);
        var url = Config.uploadHydrus;

        console.log(formData);
        await fetch(url, {
            method : "POST",
            body: formData
        }).then(response => {
            if (response.status !== 200) {
                console.log(response)
                response.json().then(value => {
                    if(value?.error !== undefined && value?.error !== null && value?.error !== "" ){
                        $('#toast-message').text(value?.error);
                        $('#error-wrong-hydrus').toast('show');
                    }
                    else {
                        $('#toast-message').text('Invalid Hydrus project');
                        $('#error-wrong-hydrus').toast('show');
                    }
                })
            } else {
                location.replace(response.url);
            }
        });
    }

    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';

        var flag = false;
        for (let i = 0; i < e.dataTransfer.files.length; i++) {
            if (models.includes(e.dataTransfer.files[i].name.split(".")[0])) {
                flag = true;
            }
        }

        if (flag === true) {
            $('#toast-message').html('Upload Hydrus model with different name');
            $('#error-wrong-hydrus').toast('show');
        } else {
            startUpload(e.dataTransfer.files);
        }
    }

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    }

    if ( $('#error-hydrus').length ){
        $('#error-hydrus').toast('show');
    }
})(jQuery);