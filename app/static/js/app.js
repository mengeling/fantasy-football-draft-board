function get_board_subset() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-board-subset/",
    contentType: "application/json; charset=utf-8",
    data: { position: $(".position-dropdown  option:selected").val(),
            player: $("input.search").val() },
    success: function(data) {
      $(".draft-board").html(data.board);
    }
  });
}


$( "select.position-dropdown" ).change(function () {
  get_board_subset();
})


$( "input.search" ).on("input", function () {
  get_board_subset();
})


$( "div.draft-board" ).on("click", "tr", function () {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/player-details/",
    contentType: "application/json; charset=utf-8",
    data: { player_id: $(this).find("td > span").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
    }
  });
})


$( "button.draft-button" ).on("click", function () {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/draft-player/",
    contentType: "application/json; charset=utf-8",
    data: { player_id: $(".player-pic").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
})


$( "input.update-rankings-button" ).on("click", function () {
  var message = "Download latest " +
      $(".scoring-options option:selected").attr("id") +
      " rankings? It may take up to 10 minutes."
  if (!confirm(message)) return false;
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-data/",
    contentType: "application/json; charset=utf-8",
    data: { scoring_option: $(".scoring-options option:selected").val() },
    success: function(data) {
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
})
