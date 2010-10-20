google.load("jquery", "1.4.3");

function top2chord_translate(url, id) {
  function handleResponse(response, status) {
    $(id).text(response);
  }
  $.post('http://localhost:8080' + url, {song: $(id).val()}, handleResponse, "text");
}
