function addaccount() {
    // Specify the URL of the page you want to open
    var anotherPageUrl = 'addaccount';

    // Open a new window with the specified URL
    var anotherPageWindow = window.open(anotherPageUrl, '_blank', 'width=600,height=400');
    
    // Optionally focus on the new window
    if (anotherPageWindow) {
        anotherPageWindow.focus();
    }
}