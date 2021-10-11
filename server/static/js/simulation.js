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
                $('#start-alert').removeAttr('hidden');
                console.log(content)
                _hydrusCalc.removeAttr('hidden');

                check_simulation_status(content["id"])
            },
            error: function (e) {
                $('#error-alert').removeAttr('hidden');
                const rsp = JSON.parse(e.responseText);
                console.log(rsp["message"])
                // TODO powiadomienie że się nie udało wystartować
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
                console.log(data)
                //TODO zatrzymać spinnery
                if (data["hydrus"]) {
                    _hydrusCalc.removeClass('text-secondary');
                    _hydrusCalc.addClass('text-success');
                    _passingCalc.removeAttr('hidden');
                }
                if (data["passing"]) {
                    _passingCalc.removeClass('text-secondary');
                    _passingCalc.addClass('text-success');
                    _modflowCalc.removeAttr('hidden');
                }
                if (data["modflow"]) {
                    _modflowCalc.removeClass('text-secondary');
                    _modflowCalc.addClass('text-success');
                    //TODO Wizualizacja
                } else {
                    setTimeout(check_simulation_status, 2000);
                }
            },
        });

    }


})(jQuery);