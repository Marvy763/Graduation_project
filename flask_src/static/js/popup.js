 //////////////////////////////////////////////////////////////
  
  ///////////              Popup Message
  
  //////////////////////////////////////////////////////////////
  window.addEventListener("load", function () {
    setTimeout(function open(event) {
      document.getElementsByClassName("popup")[0].classList.add("active");
     },
          2000
      )
  });
  
    document.getElementById("close").addEventListener(
      "click",
      function () {
        document.getElementsByClassName("popup")[0].classList.remove("active");
  });
  