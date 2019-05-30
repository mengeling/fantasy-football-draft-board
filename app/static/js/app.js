// START LOGIN FUNCTIONS
function get_data() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-data/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class") },
    success: function(data) {
      $("#draft-undraft-button").attr("class", "0");
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
}

function check_if_board_exists() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/check-if-board-exists/",
    contentType: "application/json; charset=utf-8",
    data: { username: $(".username-input").val() },
    success: function(data) {
      $("body").attr("class", data.username)
      if (data.exists == 1) {
        get_data()
        $(".username-input").val("");
        $(".login-background").hide()
      }
      else {
        $(".login-background").hide()
        $(".download-background").show()
      }
    }
  });
}
// END LOGIN FUNCTIONS



// START PLAYER SEARCH FUNCTIONS
function clear_search() {
  $(".player-search").val("");
  $(".position-dropdown").val("ALL");
  $(".team-dropdown").val("ALL");
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

function get_player_details(player_id) {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-player-details/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            player_id: player_id },
    success: function(data) {
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
    }
  });
}
// END PLAYER SEARCH FUNCTIONS



// START DRAFT PLAYER FUNCTIONS
function get_drafted_board() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get-drafted-board/",
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

function draft_undraft_player() {
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
}
// END DRAFT PLAYER FUNCTIONS



// START DOWNLOAD RANKINGS FUNCTIONS
function download_data(scoring_option) {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/download-data/",
    contentType: "application/json; charset=utf-8",
    data: { username: $("body").attr("class"),
            scoring_option: scoring_option },
    beforeSend: function() {
        $(".loader").show();
    },
    success: function(data) {
      $(".loader").hide();
      $("#draft-undraft-button").attr("class", "0");
      $(".player-pic").attr("src", data.img_url);
      $(".player-pic").attr("id", data.player_id);
      $(".player-stats").html(data.player_details);
      $(".draft-board").html(data.board);
    }
  });
}
// END DOWNLOAD RANKINGS FUNCTIONS



// START LOGIN
$(".login-button").on("click", function() {
  check_if_board_exists();
});

$(".username-input").keypress(function(event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13') {
      check_if_board_exists();
    }
});


$(".login-scoring-button").on("click", function() {
  var scoring_option = $(this).val();
  download_data(scoring_option);
  $(".username-input").val("");
  $(".download-background").hide();
})


$(".login-cancel-button").on("click", function() {
  $(".login-background").show();
  $(".download-background").hide();
});


$(".back-login-button").on("click", function() {
  $(".login-background").show();
});
// END LOGIN



// START PLAYER SEARCH
$(".position-dropdown, select.team-dropdown").change(function() {
  get_board_subset();
})


$(".player-search").on("input", function() {
  get_board_subset();
})


$(".clear-search-button").on("click", function() {
  clear_search();
  get_board_subset();
})


$(".draft-board").on("click", "tr", function() {
  var player_id = $(this).find("td > span").attr("id");
  get_player_details(player_id);
})
// END PLAYER SEARCH



// START DRAFT PLAYER
$(".available-button").on("click", function() {
  $("#draft-undraft-button").attr("class", "0");
  $("#draft-undraft-button").text("Draft Selected Player");
  clear_search();
  get_drafted_board();
})


$(".drafted-button").on("click", function() {
  $("#draft-undraft-button").attr("class", "1");
  $("#draft-undraft-button").text("Undraft Selected Player");
  clear_search();
  get_drafted_board();
})


$("#draft-undraft-button").on("click", function() {
  draft_undraft_player();
  clear_search();
})
// END DRAFT PLAYER



// START DOWNLOAD RANKINGS
$(".update-rankings-button").on("click", function() {
  $(".popup-background").show();
});


$(".popup-background").on("click", function(e) {
  if( $(e.target).closest(".popup-content").length > 0 ) {
    return
  }
  $(".popup-background").hide();
});


$(".popup-cancel-button").on("click", function() {
  $(".popup-background").hide();
});


$(".popup-scoring-button").on("click", function() {
  var scoring_option = $(this).val();
  download_data(scoring_option);
  clear_search();
  $(".popup-background").hide();
})
// END DOWNLOAD RANKINGS
