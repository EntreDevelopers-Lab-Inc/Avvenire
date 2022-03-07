function toggleRoadMap(count) {
  let element = document.getElementById(`timelinework_${count}`);
  let sideImage = document.getElementById("side_image");
  let display = element.style.display;

  sideImage.src = `/static/img/roadmap/${count}.jpg`;

  if (display === "block") {
    element.style.display = "none";
  } else {
    element.style.display = "block";
  }
}
