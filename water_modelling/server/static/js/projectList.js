// project removal
async function doDelete(projectName, wasWarned) {
    if (wasWarned) {
        var url = Config.projectList;
        await fetch(url, {
            method: "DELETE",
            body: JSON.stringify({projectName: projectName})
        }).then(response => {
            if (response.status === 200) {
                location.replace(response.url)
            }
        });
    }
    else {
        document.getElementById("deleteProjectButton").hidden = true
        document.getElementById("areYouSureButton").hidden = false
    }
}

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
