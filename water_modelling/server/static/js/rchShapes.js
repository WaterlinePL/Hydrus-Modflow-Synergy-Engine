function handleSubmit(rchShapeIdx, currentModel) {

    const hydrusModel = $("#hydrus-model").val();
    console.log(hydrusModel, currentModel);
    const nextIdx = parseInt(rchShapeIdx) + 1;

    if (hydrusModel !== null && hydrusModel !== undefined && hydrusModel !== '') {
        const formdata = {"hydrusModel": hydrusModel, "previousModel": currentModel};

        $.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(formdata),
                    dataType: 'json',
                    url: Config.rchShapes + rchShapeIdx,
                    success: function (e) {
                        $('#toast-body-success-rch-shapes').text("Model has been correctly assigned to the shape!")
                        $('#success-rch-shapes').toast('show');
                        setTimeout(function () {
                            window.location.href = Config.rchShapes + nextIdx;
                        }, 500);

                    },
                    error: function(error) {
                        $('#toast-body-error-rch-shapes').text("Cannot assign shape");
                        $('#error-rch-shapes').toast('show');
                }
         });
    } else {
        $('#toast-body-success-rch-shapes').text("Shape skipped. Redirecting to next shape!")
        $('#success-rch-shapes').toast('show');
        setTimeout(function () {
            window.location.href = Config.rchShapes + nextIdx;
        }, 500);

    }
}

function handleBackButton(rchShapeIdx) {
    console.log(`redirect to last page`);
    let lastModelId = parseInt(rchShapeIdx) - 1;
    if (lastModelId === -1) {
        window.location.href = Config.defineMethod;
    } else {
        window.location.href = Config.rchShapes + lastModelId;
    }
}