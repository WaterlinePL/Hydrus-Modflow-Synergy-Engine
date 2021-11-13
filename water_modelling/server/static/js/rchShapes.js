function handleSubmit(rchShapeIdx) {

    const hydrusModel = $("#hydrus-model").val();
    console.log(hydrusModel);

    if (hydrusModel !== null && hydrusModel !== undefined){
        const formdata = {"hydrusModel": hydrusModel};
        const nextIdx = parseInt(rchShapeIdx)+1;

        $.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(formdata),
                    dataType: 'json',
                    url: Config.rchShapes + rchShapeIdx,
                    success: function (e) {
                        $('#success-rch-shapes').toast('show');
                        setTimeout(function () {
                            window.location.href = Config.rchShapes+nextIdx;
                        }, 500);

                    },
                    error: function(error) {
                        $('#toast-body-error-rch-shapes').text("Cannot assign shape");
                        $('#error-rch-shapes').toast('show');
                }
         });
    } else {
        $('#toast-body-error-rch-shapes').text("Choose Hydrus model from list");
        $('#error-rch-shapes').toast('show');
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