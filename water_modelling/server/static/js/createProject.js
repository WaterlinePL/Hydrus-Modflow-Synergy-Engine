if ( $('#error-name').length ){
    showToast('error-name');
}

function showToast(elementId) {
    let myAlert = document.getElementById(elementId);
    let bsAlert = new bootstrap.Toast(myAlert);
    bsAlert.show();
}