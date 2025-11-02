document.addEventListener("DOMContentLoaded", function () {
    var createBtn = document.getElementById("createRequestBtn");
    var model = document.getElementById("requestModel");
    var closeBtn = document.querySelector(".close-model");

    if (createBtn && model) {
        createBtn.addEventListener("click", function () {
            model.style.display = "block";
        });

        closeBtn.addEventListener("click", function () {
            model.style.display = "none";
        });

        window.addEventListener("click", function (event) {
            if (event.target == model) {
                model.style.display = "none";
            }
        });
    } else {
        console.error("Request button or model not found!");
    }
});
function toggleDetails(id) {
    let detailsRow = document.getElementById("details-" + id);
    detailsRow.style.display = detailsRow.style.display === "none" ? "table-row" : "none";
}
function openRequestDetails(id) {
    document.getElementById("req-id").textContent = id;
    document.getElementById("req-description").textContent = id === 22 ? "Approval for Event Organization" : "Budget Approval for Tech Fest";
    document.getElementById("req-by").textContent = id === 22 ? "John Doe" : "Jane Smith";
    document.getElementById("req-status").textContent = id === 22 ? "Pending" : "Approved";
    document.getElementById("request-model").style.display = "block";
}

function closeModel() {
    document.getElementById("request-model").style.display = "none";
}

function approveRequest() {
    alert("Request Approved");
    closeModel();
}

function rejectRequest() {
    alert("Request Rejected");
    closeModel();
}

function forwardRequest() {
    alert("Request Forwarded");
    closeModel();
}


function validateLogin(event) {
    event.preventDefault();

    var userId = document.getElementById("userid").value.trim();
    var password = document.getElementById("password").value.trim();

    if (userId === "" || password === "") {
        alert("Please enter valid credentials.");
        return;
    }

    if (userId === "admin" && password === "password") {
        // Admin login
        localStorage.setItem("user", "admin");  
        window.location.href = "a_dashbd.html";
    } else {
        // Regular user login
        localStorage.setItem("user", "user"); 
        window.location.href = "u_dashbd.html";
    }
}

// Redirect unauthorized users to login page
function checkAuth() {
    var user = localStorage.getItem("user");

    if (window.location.pathname.includes("a_dashbd.html") && user !== "admin") {
        window.location.href = "index.html"; // Redirect if not admin
    } else if (window.location.pathname.includes("u_dashbd.html") && !user) {
        window.location.href = "index.html"; // Redirect if not logged in
    }
}

// Call checkAuth() when accessing protected pages
checkAuth();