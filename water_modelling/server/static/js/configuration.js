(function($) {
    'use strict'

    document.getElementById("form-modflow-hydrus").onsubmit = function (e) {
        e.preventDefault()
        var element = this.elements[0];

        const modflowExe = this.elements.modflowFile.value;
        const hydrusExe = this.elements.hydrusFile.value;

        console.log(this.elements.modflowFile.value);
        console.log(this.elements.hydrusFile.value);

        if (modflowExe !== null && modflowExe !== undefined && modflowExe.trim() !== "" &&
            hydrusExe !== null && hydrusExe !== undefined && hydrusExe.trim() !== ""){

            removeInvalid('modflowFile');
            removeInvalid('hydrusFile');
            const formdata = {"modflowExe": modflowExe.trim(), "hydrusExe": hydrusExe.trim()};
             $.ajax({
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(formdata),
                        dataType: 'json',
                        url: Config.configuration,
                        success: function (e) {
                            console.log("Paths saved")
                            $('#success-configuration').toast('show');
                            setTimeout(function () {
                                window.location.href = Config.configuration;
                            }, 500);

                        },
                        error: function(error) {
                            let errorMsg = "";
                            if (error.responseJSON && error.responseJSON.error && error.responseJSON.model) {
                                errorMsg = error.responseJSON.error;
                                const model = error.responseJSON.model;
                                console.log(model);
                                if (model === "modflow") {
                                    addInvalid('modflowFile');
                                } else if (model === "hydrus") {
                                    addInvalid('hydrusFile');
                                }
                            }
                            else {
                                errorMsg = "An unknown error occurred"
                            }
                            $('#toast-body-error-configuration').text(errorMsg);
                            $('#error-configuration').toast('show');
                    }
             });
        } else {
            $('#toast-body-error-configuration').text("Incorrect paths");
            $('#error-configuration').toast('show');
        }
    }

    function removeInvalid(elementId){
        if($(`#${elementId}`).hasClass('is-invalid')){
            $(`#${elementId}`).removeClass('is-invalid');
        }
    }

    function addInvalid(elementId){
        if(!$(`#${elementId}`).hasClass('is-invalid')){
                $(`#${elementId}`).addClass('is-invalid');
        }
    }

    function containsOnlyWhitespaces(text) {
        const pattern = /[\t\n ]/g;
        return !text.replace(pattern, '').length;
    }

    if ( !containsOnlyWhitespaces( $('#error-configuration').text() ) ){
        $('#error-configuration').toast('show');
    }

})(jQuery);