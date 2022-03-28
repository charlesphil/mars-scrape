function showLoading() {
    let progressRow = document.getElementById("progress-row");
    if (progressRow.style.display === "none") {
        progressRow.style.display = "flex";
    } else {
        progressRow.style.display = "flex";
    }
    document.getElementById("update-button").classList.add("disabled");
    document.getElementById("update-button").textContent="Updating...";
}