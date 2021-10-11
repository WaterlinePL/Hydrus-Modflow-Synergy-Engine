(function($) {
    var _container = $("#simulation-content"),
        _hydrusCalc = $('#hydrus-calc'),
        _modflowCalc = $('#modflow-calc'),
        _passingCalc = $('#passing-calc'),
        _runButton = $('#start-simulation');


    _runButton.on("click", (e) => {
        e.preventDefault()
        const url = "/run-simulation";

        // setBusy(_container);
        ($).ajax({
            url: url,
            type: "GET",
            dataType: "text",
            context: this,
            success: function (content) {
                _runButton.attr('hidden', true);
                $('#start-alert').removeAttr('hidden');

                //TODO przenieść to w jakieś miejsce które będzie odbierać sygnały z backendu
                //===============
                _hydrusCalc.removeAttr('hidden');
                _hydrusCalc.addClass('text-success');
                _passingCalc.removeAttr('hidden');
                _passingCalc.addClass('text-success');
                _modflowCalc.removeAttr('hidden');
                _modflowCalc.addClass('text-secondary');
                // ==============

                // console.log("Success")
                // clearBusy(_container);
                // TODO wyświetl info co się dzieje i powiadomienie że się udało wystartować
            },
            error: function (e) {
                $('#error-alert').removeAttr('hidden');
                // console.log("Error")
                // clearBusy(_container);
                // TODO powiadomienie że się nie udało wystartować
            }
        });
    });



})(jQuery);