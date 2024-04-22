function myFunction(event) {
    // Find the closest anchor element (TNum hyperlink) when a child element is clicked
    const clickedLink = event.target.closest('a');

    if (clickedLink) {
        // Prevent the default action of the anchor element
        event.preventDefault();
        
        // Extract the content of the TNum hyperlink
        var rowData = clickedLink.textContent;

        // Construct the URL for the editTransaction page
        var editTransactionUrl = 'editTransaction';

        // Open a popup window with the specified URL
        var popupWindow = window.open(editTransactionUrl + encodeURIComponent(rowData), 'editTransactionPopup', 'width=600,height=800');

        // Optionally focus on the popup window
        if (popupWindow) {
            popupWindow.focus();
        }
    }
}