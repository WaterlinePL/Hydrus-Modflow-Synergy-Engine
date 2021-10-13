(function($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone-modflow');

    async function startUploadModflow(files) {
        console.log("MODFLOW");
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
        this.className = 'upload-drop-zone-modflow';
        startUploadModflow(e.dataTransfer.files)
    }

    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone-modflow drop';
        return false;
    }

    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone-modflow';
        return false;
    }

    if ( $('#error-modflow').length ){
        $('#error-modflow').toast('show');
    }

})(jQuery);