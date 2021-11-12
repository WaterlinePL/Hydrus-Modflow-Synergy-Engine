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
        var url = "/upload-hydrus";
        await fetch(url, {
            method : "POST",
            body: formData
        }).then(reponse => location.replace(reponse.url));
    }

    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';

        var flag = false;
        for (let i = 0; i < e.dataTransfer.files.length; i++) {
            if (models.includes(e.dataTransfer.files[i].name.split(".")[0])) {
                flag = true;
            }
        }

        if (flag === true) {
            $('#error-wrong-hydrus').toast('show');
        } else {
            startUpload(e.dataTransfer.files);
        }
    }

    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    }

    if ( $('#error-hydrus').length ){
        $('#error-hydrus').toast('show');
    }
})(jQuery);