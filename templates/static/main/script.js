function isNumber(event) {
  return "01234567890*-/,".includes(event.key);
}

function getExpressionDescriptor() {
  var content = document.getElementById("readable");

  if (content) {
    var minute = document.getElementById("learn_schedule_minute").value;
    var hour = document.getElementById("learn_schedule_hour").value;
    var day = document.getElementById("learn_schedule_day").value;
    var month = document.getElementById("learn_schedule_month").value;
    var week = document.getElementById("learn_schedule_week").value;

    content.innerText = cronstrue.toString(
      minute + " " + hour + " " + day + " " + month + " " + week,
      { use24HourTimeFormat: true, locale: "pt_BR" }
    );
  }
}

function focusCron(label) {
  document.getElementById(label).style.color = "var(--link)";
  document.getElementById(label + "-explain").style.display = "block";
}

function blurCron(label) {
  document.getElementById(label).style.color = "var(--text)";
  document.getElementById(label + "-explain").style.display = "none";
}

function toggleCollapsed() {
  var element = document.querySelector("body");
  element.classList.toggle("collapsed");
  localStorage.setItem("collapsed", element.classList.contains("collapsed"));
}

window.addEventListener(
  "load",
  function () {
    getExpressionDescriptor();
  },
  false
);

//function toggle_visibility() {
//    var x = document.getElementById("trash-button");
//
//    if (x.style.display === "none") {
//        x.style.display = "block";
//    } else {
//        x.style.display = "none";
//    }
//};