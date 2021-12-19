
function initializeArray(rows, cols) {
    return Array(rows).fill(0).map(() => Array(cols).fill(0));
}

let rows_all =  document.getElementsByClassName("cell-row");
let rows_total = rows_all.length
let columns_total = rows_all[0].children.length
console.log("rows: " + rows_total);
console.log("columns: " + columns_total);

let shapeArray = initializeArray(rows_total, columns_total);
let addCellInDirection = 0;

if ( $('#error-shapes') && $('#error-shapes').length ){
    showToast('error-shapes');
}

function handleSubmit(modelIdx) {
    for (let i = 0; i < rows_total; i++) {
        for (let j = 0; j < columns_total; j++) {
            shapeArray[i][j] = document.getElementById(`cell_${i}_${j}`).classList.contains("bg-primary") ? 1 : 0;
        }
    }

    let request = new XMLHttpRequest();
    request.open("POST", Config.manualShapes + `${modelIdx}`, true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    request.onload = function () {
        let response = JSON.parse(this.responseText);
        if (response && response.status === "OK") {
            showToast('successMessage');
            let nextModelId = parseInt(modelIdx) + 1;
            setTimeout(function () {
                console.log("redirecting to next model...");
                window.location.href = Config.manualShapes + nextModelId;
            }, 500);

        }
    }

    request.send(JSON.stringify(shapeArray));
}

function handleBackButton(modelIdx) {
    console.log(`redirect to last page`);
    let lastModelId = parseInt(modelIdx) - 1;
    if (lastModelId === -1) {
        window.location.href = Config.defineMethod;
    } else {
        window.location.href = Config.manualShapes + lastModelId;
    }
}

function showToast(elementId) {
    let myAlert = document.getElementById(elementId);
    let bsAlert = new bootstrap.Toast(myAlert);
    bsAlert.show();
}

function getRowColFromId(cellId) {
    let cell = cellId.split('_');
    return {"row": parseInt(cell[1]), "col": parseInt(cell[2])}
}

function onMouseOver(id, isHighlighted) {
    const grid = getRowColFromId(id);
    const row = grid.row;
    const col = grid.col;

    for (let i = row - addCellInDirection; i <= row + addCellInDirection; i++) {
        for (let j = col - addCellInDirection; j <= col + addCellInDirection; j++) {
            if (i < 0 || i >= rows_total || j < 0 || j >= columns_total) {
                continue;
            }
            document.getElementById(`cell_${i}_${j}`).classList.toggle("bg-primary", isHighlighted);
        }
    }
}

$(function () {

    let isMouseDown = false, isHighlighted;
    $("#model-mesh td")
        .mousedown(function () {
            isMouseDown = true;
            isHighlighted = !$(this).hasClass("bg-primary");
            onMouseOver(this.id, isHighlighted);
            return false; // prevent text selection
        })
        .mouseover(function () {
            if (isMouseDown) {
                onMouseOver(this.id, isHighlighted);
            }
        })
        .bind("selectstart", function () {
            return false;
        })

    $(document)
        .mouseup(function () {
            isMouseDown = false;
        });

    $("#brush-size").ready(function(){
        addCellInDirection = parseInt($("#brush-size").val());
        $("#brush-size").change(function (){
            addCellInDirection = parseInt($("#brush-size").val());
        })
    })
});