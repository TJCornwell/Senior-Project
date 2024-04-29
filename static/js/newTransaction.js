function newTransaction() {
    // Specify the URL of the page you want to open
    var anotherPageUrl = 'newTransaction';

    // Open a new window with the specified URL
    var anotherPageWindow = window.open(anotherPageUrl, '_blank', 'width=600,height=800');
    
    // Optionally focus on the new window
    if (anotherPageWindow) {
        anotherPageWindow.focus();
    }
}