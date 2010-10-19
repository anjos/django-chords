google.load("jquery", "1.3");

function top2chord_translate(url) {
  function handleResponse(response, status) {
    $("#id_song").text(response);
  }
  $.post(url, {song: $("#id_song").text()}, handleResponse, "text");
}
