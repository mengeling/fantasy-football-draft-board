function clear_search() {
  $("input.search").val("");
  $("select.position-dropdown").val("ALL");
  $("select.team-dropdown").val("ALL");
}


function get_player_full_board() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-player-full-board/",
    contentType: "application/json; charset=utf-8",
    data: { drafted: $("#draft-undraft-button").attr("class") },
    success: function(data) {
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
}


function get_board_subset() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-board-subset/",
    contentType: "application/json; charset=utf-8",
    data: { drafted: $("#draft-undraft-button").attr("class"),
            position: $(".position-dropdown  option:selected").val(),
            team: $(".team-dropdown  option:selected").val(),
            name: $("input.search").val() },
    success: function(data) {
      $(".draft-board").html(data.board);
    }
  });
}


$( "select.position-dropdown, select.team-dropdown" ).change(function () {
  get_board_subset();
})


$( "input.search" ).on("input", function () {
  get_board_subset();
})


$( "button.available-button" ).on("click", function () {
  $("#draft-undraft-button").attr("class", "0");
  $("#draft-undraft-button").text("Draft Selected Player");
  clear_search()
  get_player_full_board();
})


$( "button.drafted-button" ).on("click", function () {
  $("#draft-undraft-button").attr("class", "1");
  $("#draft-undraft-button").text("Undraft Selected Player");
  clear_search()
  get_player_full_board();
})


$( "button.clear-search-button" ).on("click", function () {
  clear_search();
  get_board_subset()
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


$( "button#draft-undraft-button" ).on("click", function () {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/draft-undraft-player/",
    contentType: "application/json; charset=utf-8",
    data: { drafted: $("#draft-undraft-button").attr("class"),
            player_id: $(".player-pic").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
  clear_search();
})


$( "input.update-rankings-button" ).on("click", function () {
  var message = "Download latest " +
      $(".scoring-options option:selected").attr("id") +
      " rankings? It may take up to 10 minutes."
  if (!confirm(message)) return false;
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/update-data/",
    contentType: "application/json; charset=utf-8",
    data: { scoring_option: $(".scoring-options option:selected").val() },
    success: function(data) {
      $("#draft-undraft-button").attr("class", "0");
      $(".player-pic").attr("src", "/static/img/" + data.player_id + ".jpg");
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
  clear_search();
})
