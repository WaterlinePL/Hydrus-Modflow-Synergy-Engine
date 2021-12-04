(function ($) {

    document.getElementById("form-create-project").onsubmit = function (e) {
        e.preventDefault()
        console.log(this.elements)
        const name = this.elements.name.value;
        const lat = this.elements.lat.value;
        const long = this.elements.long.value;
        const startDate = this.elements.startDate.value;
        const endDate = this.elements.endDate.value;
        const spinUp = this.elements.spinUp.value;

        if (isTextCorrect(name, 'name') &&
            isCoordCorrect(lat, 'lat') &&
            isCoordCorrect(long, 'long') &&
            isSpinUpCorrect(spinUp, 'spinUp') &&
            checkDates(startDate, 'startDate', endDate, 'endDate')){

            const formdata = {
                "name": name.trim(),
                "lat": lat,
                "long": long,
                "start_date": startDate,
                "end_date": endDate,
                "spin_up": spinUp
            };
            
            if (this.elements[6].value === "Create") {
                createProject(formdata);
            } else if(this.elements[6].value === "Update") {
                updateProject(formdata);
            }

        } else {
            $('#toast-body-error').text('Provide correct data')
            $('#error').toast('show');
        }
    }

    function updateProject(formdata) {
        console.log("update");
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formdata),
            dataType: 'json',
            url: Config.editProject+formdata.name,
            success: function (e) {
                $('#toast-success').text('Project successfully updated!')
                $('#success-project-create').toast('show');
                setTimeout(function () {
                    window.location.href = Config.currentProject+"/"+formdata.name;
                }, 500);
            },
            error: function (error) {
                const errorMsg = error.responseJSON.error;
                addInvalid('name');
                $('#toast-body-error').text(errorMsg);
                $('#error').toast('show');
            }
        });
    }

    function createProject(formdata) {
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formdata),
            dataType: 'json',
            url: Config.createProject,
            success: function (e) {
                $('#toast-success').text('Project have been successfully created!');
                $('#success-project-create').toast('show');
                setTimeout(function () {
                    window.location.href = Config.currentProject;
                }, 500);
            },
            error: function (error) {
                const errorMsg = error.responseJSON.error;
                addInvalid('name');
                $('#toast-body-error').text(errorMsg);
                $('#error').toast('show');
            }
        });
    }

    function checkDates(firstDate, firstDateId, secondDate, secondDateId) {
        if( isDateCorrect(firstDate, firstDateId) &&
            isDateCorrect(secondDate, secondDateId)){
            const firstDateParse = new Date(firstDate);
            const secondDateParse = new Date(secondDate);
            console.log(firstDateParse, secondDateParse);

            if(secondDateParse > firstDateParse){
                removeInvalid(firstDateId);
                removeInvalid(secondDateId);
                return true;
            } else {
                addInvalid(firstDateId);
                addInvalid(secondDateId);
            }
        }
        return false;
    }

    function isDateCorrect(date, elementId) {
        if (date.match(/^(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$/g, date)) {
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }
    }

    function isCoordCorrect(coord, elementId) {
        if (coord.match(/^[-]?(0|[1-9][0-9]*)([.]\d+)?$/g, coord)) {
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }

    }

    function isTextCorrect(text, elementId) {
        if (text !== null && text !== undefined && text.trim() !== "") {
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }
    }

    function isSpinUpCorrect(spinUp, elementId) {
        if (spinUp.match(/^[\d.]+(?:e-?\d+)?$/g, spinUp)) {
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }
    }

    function removeInvalid(elementId) {
        if ($(`#${elementId}`).hasClass('is-invalid')) {
            $(`#${elementId}`).removeClass('is-invalid');
        }
    }

    function addInvalid(elementId) {
        if (!$(`#${elementId}`).hasClass('is-invalid')) {
            $(`#${elementId}`).addClass('is-invalid');
        }
    }
})(jQuery);
