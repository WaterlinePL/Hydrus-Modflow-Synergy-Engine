(function($) {
    'use strict'

    document.getElementById("form-search").onsubmit = function (e) {
        e.preventDefault();

        const search = this.elements.search.value;
        console.log(this.elements.search.value);
        if( search !== null && search !== undefined && search.trim() !== "") {
            window.location.href = Config.projectList+"/"+search;
        } else {
            window.location.href = Config.projectList;
        }
    }

    $('#error').toast('show');

})(jQuery);
