function clear_search() {
  $(".player-search").val("");
  $(".position-dropdown").val("ALL");
  $(".team-dropdown").val("ALL");
}


function get_player_full_board() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-player-full-board/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            drafted: $("#draft-undraft-button").attr("class") },
    success: function(data) {
      $(".player-pic").attr("src", data.img_url);
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
    data: { username: $("body").attr("class"),
            drafted: $("#draft-undraft-button").attr("class"),
            position: $(".position-dropdown  option:selected").val(),
            team: $(".team-dropdown  option:selected").val(),
            name: $(".player-search").val() },
    success: function(data) {
      $(".draft-board").html(data.board);
    }
  });
}


$(".position-dropdown, select.team-dropdown").change(function() {
  get_board_subset();
})


$(".player-search").on("input", function() {
  get_board_subset();
})


$(".available-button").on("click", function() {
  $("#draft-undraft-button").attr("class", "0");
  $("#draft-undraft-button").text("Draft Selected Player");
  clear_search()
  get_player_full_board();
})


$(".drafted-button").on("click", function() {
  $("#draft-undraft-button").attr("class", "1");
  $("#draft-undraft-button").text("Undraft Selected Player");
  clear_search()
  get_player_full_board();
})


$(".clear-search-button").on("click", function() {
  clear_search();
  get_board_subset()
})


$(".draft-board").on("click", "tr", function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/player-details/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            player_id: $(this).find("td > span").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
    }
  });
})


$("#draft-undraft-button").on("click", function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/draft-undraft-player/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            drafted: $("#draft-undraft-button").attr("class"),
            player_id: $(".player-pic").attr("id") },
    success: function(data) {
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
  clear_search();
})


$(".update-rankings-button").on("click", function() {
  $(".popup-background").show();
});


$(".popup-background").on("click", function(e) {
  if( $(e.target).closest(".popup-content").length > 0 ) {
    return
  }
  $(".popup-background").hide();
});


$(".popup-cancel-button").on("click", function(e) {
  $(".popup-background").hide();
});


$(".popup-scoring-button").on("click", function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/update-data/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            scoring_option: $(this).val() },
    beforeSend: function() {
        $(".loader").show();
    },
    success: function(data) {
      $(".loader").hide();
      $(".popup-background").hide();
      $("#draft-undraft-button").attr("class", "0");
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
  clear_search();
})


$(".login-back-button").on("click", function(e) {
  $(".login-background").show()
  $(".download-background").hide()
});


$(".login-scoring-button").on("click", function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-data/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            scoring_option: $(this).val() },
    beforeSend: function() {
        $(".loader").show();
    },
    success: function(data) {
      window.location.href = "/draft-board/" + data.username;
    }
  });
})


$(".login-button").on("click", function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/check-if-board-exists/",
    contentType: "application/json; charset=utf-8",
    data: { username: $(".username-input").val() },
    success: function(data) {
      if (data.exists == 1) {
        window.location.href = "/draft-board/" + data.username;
      }
      else {
        $("body").attr("class", data.username)
        $(".login-background").hide()
        $(".download-background").show()
      }
    }
  });
});
