$( ".draft-board tr" ).click(function () {
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
