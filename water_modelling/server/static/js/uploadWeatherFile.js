
(function ($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone-modflow');

    async function startUploadWeatherFile(files, model_name) {
        const formData = new FormData();
        const file = files[0];
        formData.append('file', file);
        formData.append('model_name', model_name)
        var url = Config.uploadWeatherFile;
        await fetch(url, {
            method: "POST",
            body: formData
        }).then(response => {
            if (response.status !== 200) {
                response.json().then(function(data) {
                    if (data && data.error) $('#error-toast-message').html(data.error);
                    else $('#error-toast-message').html('An unknown error occurred');
                    $("#error-toast").toast('show');
                });
            } else {
                $("#success-toast").toast('show');
            }
        });
    }

    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        let model_name = document.getElementById("model-select").value
        startUploadWeatherFile(e.dataTransfer.files, model_name)
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