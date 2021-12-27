(function ($) {
    var _container = $("#simulation-content"),
        _hydrusCalc = $('#hydrus-calc'),
        _modflowCalc = $('#modflow-calc'),
        _passingCalc = $('#passing-calc'),
        _runButton = $('#start-simulation');
        _hydrusButton = $('#hydrus-button');
        _modflowButton = $('#modflow-button');


    _runButton.on("click", (e) => {
        e.preventDefault();
        const url = Config.simulationRun;

        // setBusy(_container);
        ($).ajax({
            url: url,
            type: "GET",
            dataType: "json",
            context: this,
            success: function (content) {
                _runButton.attr('hidden', true);
                $('#download').attr('hidden', true);
                $('#start-alert').toast('show');
                _hydrusCalc.removeAttr('hidden');
                checkSimulationStatus(content["id"]);
            },
            error: function (e) {
                $('#error-alert').toast('show')
                const rsp = JSON.parse(e.responseText);
                const msg = rsp["message"] ? rsp["message"] : "An unknown error occurred";
                $('#toast-body-error').text(msg);
            }
        });
    });

    function checkSimulationStatus(id) {
        const url = Config.simulationCheck + id;

        ($).ajax({
            url: url,
            type: "GET",
            dataType: "json",
            success: function (data) {
                const stopCheckingSimulation = handleHydrusResponse(data)
                                                || handlePassingResponse(data)
                                                || handleModflowResponse(data);

                if (!stopCheckingSimulation) {
                    setTimeout(checkSimulationStatus, 2000,[id]);
                }
            },
            error: function (e) {
                setTimeout(checkSimulationStatus, 2000, [id]);
            }
        });
    }

    function handleHydrusResponse (data) {
        var stopCheckingSimulation = false;
        if (isHydrusFinished(data)) {
            _hydrusCalc.removeClass('text-secondary');
            $('#hydrus-spinner').attr('hidden', true);
            const errors = getHydrusErrors(data);

            if (errors.length != 0) {
                _hydrusCalc.addClass('text-danger');
                $('#hydrus-x').removeAttr('hidden');
                _hydrusButton.removeAttr('hidden');
                stopCheckingSimulation = true;
                showErrors(errors);
            } else {
                _hydrusCalc.addClass('text-success');
                _passingCalc.removeAttr('hidden');
                $('#hydrus-tick').removeAttr('hidden');
            }
        }
        return stopCheckingSimulation;
    }

    function handlePassingResponse (data) {
        var stopCheckingSimulation = false;
        if (isPassingFinished(data)) {
            _passingCalc.removeClass('text-secondary');
            $('#passing-spinner').attr('hidden', true);
            const errors = getPassingErrors(data);

            if (errors.length != 0) {
                _passingCalc.addClass('text-danger');
                $('#passing-x').removeAttr('hidden');
                _modflowButton.removeAttr('hidden');
                stopCheckingSimulation = true;
                showErrors(errors);
            } else {
                _passingCalc.addClass('text-success');
                _modflowCalc.removeAttr('hidden');
                $('#passing-tick').removeAttr('hidden');
            }
        }
        return stopCheckingSimulation;
    }

    function handleModflowResponse (data) {
        var stopCheckingSimulation = false;
        if (isModflowFinished(data)) {
            _modflowCalc.removeClass('text-secondary');
            $('#modflow-spinner').attr('hidden', true);
            const errors = getModflowErrors(data);
            stopCheckingSimulation = true;

            if (errors.length != 0) {
                _modflowCalc.addClass('text-danger');
                _modflowButton.removeAttr('hidden');
                $('#modflow-x').removeAttr('hidden');
                showErrors(errors);
            } else {
                _modflowCalc.addClass('text-success');
                $('#modflow-tick').removeAttr('hidden');
                $('#download').removeAttr('hidden');
            }
        }
        return stopCheckingSimulation;
    }

    function isHydrusFinished (data) {
        return data["hydrus"]["finished"];
    }

    function isPassingFinished (data) {
        return data["passing"]["finished"];
    }

    function isModflowFinished (data) {
        return data["modflow"]["finished"];
    }

    function getHydrusErrors (data) {
        return data["hydrus"]["errors"];
    }

    function getPassingErrors (data) {
        return data["passing"]["errors"];
    }

    function getModflowErrors (data) {
        return data["modflow"]["errors"];
    }

    function showErrors (errors) {
        const parsedErrors = errors.join("</br>");
        $('#toast-body-error').html(parsedErrors);

        $('#error-alert').toast({autohide: false});
        $('#error-alert').toast('show');
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