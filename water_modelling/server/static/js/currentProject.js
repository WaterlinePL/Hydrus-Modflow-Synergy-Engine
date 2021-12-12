(function ($) {
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