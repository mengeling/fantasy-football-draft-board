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


$( "div.draft-board" ).on("click", "tr", function () {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/player-details/",
    contentType: "application/json; charset=utf-8",
    data: { player_id: $(this).find("td > span").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", "/static/" + data.img_path);
      $(".player-stats").html(data.player_details);
    }
  });
})


$( "select.position-dropdown" ).change(function () {
  get_board_subset();
})


$( "input.search" ).on("input", function () {
  get_board_subset();
})
