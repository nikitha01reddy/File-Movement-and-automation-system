// Show/hide details row by ID
// Show/hide details row by ID
function toggleDetails(rowId) {
    const detailsRow = document.getElementById("details-" + rowId);
    if (detailsRow) {
        detailsRow.style.display = (detailsRow.style.display === "none" || detailsRow.style.display === "") ? "table-row" : "none";
    } else {
        console.error(`Details row with ID 'details-${rowId}' not found`);
    }
}
// DOM Content Loaded actions
document.addEventListener("DOMContentLoaded", function () {
    // Hide all details rows initially
    document.querySelectorAll('.details-row').forEach(row => {
        row.style.display = 'none';
    });

    // Model and button checks
    let createBtn = document.getElementById("createRequestBtn");
    let model = document.getElementById("requestModel");
    let closeBtn = document.querySelector(".close-model");

    if (createBtn && model) {
        createBtn.addEventListener("click", () => model.style.display = "block");
        closeBtn.addEventListener("click", () => model.style.display = "none");
        window.addEventListener("click", event => {
            if (event.target == model) model.style.display = "none";
        });
    }

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            const sendTo = document.getElementById("sendTo").selectedOptions;
            const approverNoInput = document.getElementById("approverNo");
            const approverNos = approverNoInput.value ? approverNoInput.value.split(",") : [];

            if (sendTo.length !== approverNos.length) {
                event.preventDefault();
                alert("The number of approvers must match the number of approver numbers.");
            }
        });
    }

    const availableUsers = document.getElementById("availableUsers");
    const selectedUsers = document.getElementById("selectedUsers");
    const addUserButton = document.getElementById("addUser");
    const removeUserButton = document.getElementById("removeUser");

    if (addUserButton && removeUserButton && availableUsers && selectedUsers) {
        addUserButton.addEventListener("click", () => moveSelectedOptions(availableUsers, selectedUsers));
        removeUserButton.addEventListener("click", () => moveSelectedOptions(selectedUsers, availableUsers));
    }

    function moveSelectedOptions(fromSelect, toSelect) {
        Array.from(fromSelect.selectedOptions).forEach(option => {
            option.selected = true;
            toSelect.appendChild(option);
        });
    }

    // Attachments dropdown (if any)
    document.querySelectorAll('.attachments-dropdown').forEach(dropdown => {
        dropdown.addEventListener('click', function (e) {
            e.stopPropagation();
            const content = this.querySelector('.dropdown-content');
            content.style.display = content.style.display === 'block' ? 'none' : 'block';
        });
    });

    window.addEventListener('click', function () {
        document.querySelectorAll('.dropdown-content').forEach(content => {
            content.style.display = 'none';
        });
    });

    checkAuth();
});

// Request model functions
function openRequestDetails(id) {
    let requestRow = document.getElementById("request-" + id);
    if (!requestRow) {
        alert("Request details not found.");
        return;
    }

    document.getElementById("req-id").textContent = id;
    document.getElementById("req-description").textContent = requestRow.getAttribute("data-description") || "No description available";
    document.getElementById("req-by").textContent = requestRow.getAttribute("data-user") || "Unknown user";
    document.getElementById("req-status").textContent = requestRow.getAttribute("data-status") || "Status unavailable";
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

function checkAuth() {
    const user = localStorage.getItem("user");
    if (window.location.pathname.includes("a_dashbd.html") && user !== "admin") {
        window.location.href = "index.html";
    } else if (window.location.pathname.includes("u_dashbd.html") && !user) {
        window.location.href = "index.html";
    }
}

