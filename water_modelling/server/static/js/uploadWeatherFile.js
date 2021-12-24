
(function ($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone-modflow');

    $('#model-select').on('change', function() {
      var value = $(this).val();
      removeInvalid('model-select');
    });

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
                })
                .catch(function(error) {
                    $('#error-toast-message').html('An unknown error occurred');
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
        const model_name = document.getElementById("model-select").value;
        if( model_name !== undefined && model_name !== null && model_name !== ""){
            startUploadWeatherFile(e.dataTransfer.files, model_name)
        } else {
            addInvalid("model-select", "Choose model from list")
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

    function removeInvalid(elementId) {
        if ($(`#${elementId}`).hasClass('is-invalid')) {
            $(`#${elementId}`).removeClass('is-invalid');
        }
    }

    function addInvalid(elementId, errorText) {
        if (!$(`#${elementId}`).hasClass('is-invalid')) {
            $(`#${elementId}`).addClass('is-invalid');
        }

        $('#error-toast-message').text(errorText)
        $('#error-toast').toast('show');
    }

})(jQuery);