(function ($) {
    var _container = $("#simulation-content"),
        _hydrusCalc = $('#hydrus-calc'),
        _modflowCalc = $('#modflow-calc'),
        _passingCalc = $('#passing-calc'),
        _runButton = $('#start-simulation');


    _runButton.on("click", (e) => {
        e.preventDefault()
        const url = "/simulation-run";

        // setBusy(_container);
        ($).ajax({
            url: url,
            type: "GET",
            dataType: "json",
            context: this,
            success: function (content) {
                _runButton.attr('hidden', true);
                $('#start-alert').toast('show');
                _hydrusCalc.removeAttr('hidden');
                check_simulation_status(content["id"])
            },
            error: function (e) {
                $('#error-alert').toast('show')
                const rsp = JSON.parse(e.responseText);
                $('#toast-body-error').text(rsp["message"])
            }
        });
    });

    function check_simulation_status(id) {
        const url = "/simulation-check/" + id;

        ($).ajax({
            url: url,
            type: "GET",
            dataType: "json",
            success: function (data) {
                if (data["hydrus"]) {
                    _hydrusCalc.removeClass('text-secondary');
                    _hydrusCalc.addClass('text-success');
                    _passingCalc.removeAttr('hidden');
                    $('#hydrus-tick').removeAttr('hidden');
                    $('#hydrus-spinner').attr('hidden', true);
                }
                if (data["passing"]) {
                    _passingCalc.removeClass('text-secondary');
                    _passingCalc.addClass('text-success');
                    _modflowCalc.removeAttr('hidden');
                    $('#passing-tick').removeAttr('hidden');
                    $('#passing-spinner').attr('hidden', true);
                }
                if (data["modflow"]) {
                    _modflowCalc.removeClass('text-secondary');
                    _modflowCalc.addClass('text-success');
                    $('#modflow-tick').removeAttr('hidden');
                    $('#modflow-spinner').attr('hidden', true);
                    $('#download').removeAttr('hidden');
                } else {
                    setTimeout(check_simulation_status, 2000,[id]);
                }
            },
            error: function (e) {
                setTimeout(check_simulation_status, 2000, [id]);
            }
        });
    }

})(jQuery);