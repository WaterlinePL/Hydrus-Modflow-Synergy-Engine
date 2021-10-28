(function($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

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
        startUpload(e.dataTransfer.files);
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