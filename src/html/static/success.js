function successFunction() {
    var y = document.getElementById("snackbar");
    
    y.className = "show";

    setTimeout(function(){ y.className = y.className.replace("show", ""); }, 3000);
    }