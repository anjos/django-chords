google.load("jquery", "1.4.3");

function top2chord_translate(url, id) {
  function handleResponse(response, status) {
    $(id).text(response);
  }
  $.post(url, {song: $(id).val()}, handleResponse, "text");
}
