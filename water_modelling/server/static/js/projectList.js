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
    } else {
        document.getElementById("projectNameModal").innerText = projectName;
        document.getElementById("confirmDelete").onclick = function() {
            doDelete(projectName, true);
        };
    }
}

(function ($) {
    'use strict'

    document.getElementById("form-search").onsubmit = function (e) {
        e.preventDefault();

        const search = this.elements.search.value;
        console.log(this.elements.search.value);
        if (search !== null && search !== undefined && search.trim() !== "") {
            window.location.href = Config.projectList + "/" + search;
        } else {
            window.location.href = Config.projectList;
        }
    }

    $('#error').toast('show');

    $(document).ready(function () {
        $(".download").each(function (i, obj) {
            const url = Config.projectFinished + "/" + obj.id;
            ($).ajax({
                url: url,
                type: "GET",
                dataType: "json",
                context: this,
                success: function (content) {
                    if(content["status"] === "OK")
                    {
                        $(this).removeAttr('hidden')
                    }
                }
            });
        });
    });

})(jQuery);
