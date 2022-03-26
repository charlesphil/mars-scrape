function showLoading() {
    let progressRow = document.getElementById("progress-row");
    if (progressRow.style.display === "none") {
        progressRow.style.display = "flex";
    } else {
        progressRow.style.display = "none";
    }
}