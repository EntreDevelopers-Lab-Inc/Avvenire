function toggleRoadMap(count) {
  let element = document.getElementById(`timelinework_${count}`);
  let sideImage = document.getElementById("side_image");
  let display = element.style.display;

  var newSrc = location + `/static/img/roadmap/${count}.PNG`

  if (sideImage.src != newSrc)
  {
    //$(sideImage).hide(3);
    sideImage.src = newSrc;
    //$(sideImage).show(3);
  }

  if (display === "block") {
    element.style.display = "none";
  } else {
    element.style.display = "block";
  }
}

