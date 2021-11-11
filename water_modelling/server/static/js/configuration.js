(function($) {

    document.getElementById("form-modflow-hydrus").onsubmit = function (e) {
        e.preventDefault()
        var element = this.elements[0];

        const modflowExe = this.elements.modflowFile.value;
        const hydrusExe = this.elements.hydrusFile.value;

        console.log(this.elements.modflowFile.value);
        console.log(this.elements.hydrusFile.value);

        if (modflowExe !== null && modflowExe !== undefined && modflowExe.trim() !== "" &&
            hydrusExe !== null && hydrusExe !== undefined && hydrusExe.trim() !== ""){

            const formdata = {"modflowExe": modflowExe, "hydrusExe": hydrusExe};
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
                            const errorMsg = error.responseJSON.error;
                            $('#toast-body-error-configuration').text(errorMsg);
                            $('#error-configuration').toast('show');
                    }
             });
        } else {
            $('#toast-body-error-configuration').text("Incorrect paths");
            $('#error-configuration').toast('show');
        }
    }



})(jQuery);