// model removal
async function doDelete(modelName) {
    var url = Config.uploadModflow;
    await fetch(url, {
        method: "DELETE",
        body: JSON.stringify({modelName: modelName})
    }).then(response => {
        if (response.status === 200) {
            location.replace(response.url)
        }
    });
}

(function ($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone-modflow');

    async function startUploadModflow(files) {
        const formData = new FormData();
        const file = files[0];
        formData.append('archive-input', file);
        var url = Config.uploadModflow;
        await fetch(url, {
            method: "POST",
            body: formData
        }).then(response => {
            if (response.status !== 200) {
                $('#toast-message').html('Invalid modflow project');
                $("#error-wrong-modflow").toast('show');
            } else {
                location.replace(response.url)
            }
        });
    }

    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        startUploadModflow(e.dataTransfer.files)
    }

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    }

    if ( $('#error-modflow').length ){
        $('#error-modflow').toast('show');
    }

})(jQuery);