(function ($) {
    var _container = $("#simulation-content"),
        _hydrusCalc = $('#hydrus-calc'),
        _modflowCalc = $('#modflow-calc'),
        _passingCalc = $('#passing-calc'),
        _runButton = $('#start-simulation');


    _runButton.on("click", (e) => {
        e.preventDefault()
        const url = Config.simulationRun;

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
                const msg = rsp["message"] ? rsp["message"] : "An unknown error occurred";
                $('#toast-body-error').text(msg)
            }
        });
    });

    function check_simulation_status(id) {
        const url = Config.simulationCheck + id;

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

    $(document).ready(function () {
        const url = Config.projectFinished;
        ($).ajax({
            url: url,
            type: "GET",
            dataType: "json",
            context: this,
            success: function (content) {
                if(content["status"] === "OK")
                {
                    $("#download").removeAttr('hidden');
                }
            }
        });
    });

})(jQuery);