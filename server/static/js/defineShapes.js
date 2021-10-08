
function initializeArray(rows, cols) {
    return Array(rows).fill().map(() => Array(cols).fill(0));
}

function handleClick(row, col) {

    let cell = document.getElementById(`cell_${row}_${col}`);
    shapeArray[row][col] = shapeArray[row][col] ? 0 : 1;
    cell.style.backgroundColor = shapeArray[row][col] ? "red" : "white";

    console.log(shapeArray);

}

let rows_all =  document.getElementsByClassName("row");
let rows_total = rows_all.length
let columns_total = rows_all[0].children.length
console.log("rows: " + rows_total);
console.log("columns: " + columns_total);

let shapeArray = initializeArray(rows_total,columns_total);//{{rowAmount|safe}}, {{colAmount|safe}});


function handleSubmit(modelIdx) {

    let request = new XMLHttpRequest();
    request.open("POST", `/define-shapes/${modelIdx}`, true);
    request.setRequestHeader("Content-type","application/x-www-form-urlencoded");

    request.onload = function() {
        let response = JSON.parse(this.responseText);
        if (response.status === "OK") {
            document.getElementById("submitButton").style.visibility = "hidden";
            document.getElementById("successMessage").style.visibility = "visible";
            document.getElementById("nextModelButton").style.visibility = "visible";
        }
    }

    request.send(JSON.stringify(shapeArray));

}

function handleNextModel(modelIdx) {
    console.log("redirecting to next model...");
    window.location.href = '/define-shapes/' + modelIdx;
}
