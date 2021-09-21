(function($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');

    async function startUpload(files) {
        const formData = new FormData();
        const file = files[0];
        formData.append('archive-input', file);
        var url = "/upload-modflow";
        await fetch(url, {
            method : "POST",
            body: formData
        }).then(reponse => location.replace(reponse.url));
    }

    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        startUpload(e.dataTransfer.files)
    }

    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    }

})(jQuery);