function validateForm(event) {
    var fromDate = document.getElementById('fromDate').value.trim();
    var toDate = document.getElementById('toDate').value.trim();

    // Validate date format if either "from" date or "to" date is provided
    if ((fromDate !== '' && !isValidDateFormat(fromDate)) || (toDate !== '' && !isValidDateFormat(toDate))) {
        alert('Date format should be YYYY-MM-DD.');
        event.preventDefault(); // Prevent form submission
        return;
    }

    // If both "from" date and "to" date are provided, validate date range
    if (fromDate !== '' && toDate !== '') {
        var fromDateObj = new Date(fromDate);
        var toDateObj = new Date(toDate);

        // Validate that "from" date is before or equal to "to" date
        if (fromDateObj > toDateObj) {
            alert('"From" date cannot be after "to" date.');
            event.preventDefault(); // Prevent form submission
            return;
        }
    }
}

// Function to validate date format (YYYY-MM-DD)
function isValidDateFormat(dateString) {
    var dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    return dateRegex.test(dateString);
}

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('date_form');
    form.addEventListener('submit', validateForm);
});
