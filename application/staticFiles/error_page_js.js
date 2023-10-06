document.querySelector('.error-code').addEventListener('mouseover', function() {
    document.querySelector(".error-code").classList.add("active");
    
    
      setTimeout(function() {
      document.querySelector('.buggg').style.opacity = '1';
    }, 500);
    
    setTimeout(function() {
      document.querySelector(".error-code").classList.remove("active");
      document.querySelector('.buggg').style.opacity = '0';
    }, 6500);
    
    
  
  });
  
  // const errorCode = document.querySelector(".error-code");
  
  // errorCode.addEventListener("mouseover", () => {
  //   errorCode.classList.add("active");
  // });
  
  // errorCode.addEventListener("mouseout", () => {
  //   errorCode.classList.remove("active");
  // });
  
  
  