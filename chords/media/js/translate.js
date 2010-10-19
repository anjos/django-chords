function top2chord_translate() {
  function handleResponse(response, status) {
    $("#id_song").text(response);
  }
  $.post(url, {song: $("#id_song").text()}, handleResponse, "text");
}
