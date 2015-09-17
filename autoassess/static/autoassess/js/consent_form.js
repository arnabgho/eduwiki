/**
 * Created by moonkey on 8/27/15.
 */


$(document).ready(function () {
    var consent_input_form = $("#consent_input_form");
    var consent_form_content = $("#consent_form_content");
    var question_area = $('#question_area');

    var user_consent = false;

    question_area.hide();
    consent_input_form.submit(function (e) {
        e.preventDefault();
        consent_form_content.hide();
        question_area.show();

        var x_coord = 0;
        var y_coord = 0;
        window.scrollTo(x_coord, y_coord);

        user_consent = true;
        // The time should be start only after this if there is the
        // consent form session
        start_time = Date.now();
    });

    $(document).on('mouseleave', function () {
        if (user_consent) {
            console.log('mouse exited');
//            alert("You cannot leave this page before you submit.");
        }
    });


    $(window).blur(function () {
        if (user_consent) {
            var leave_message = "Please do not leave the page during the " +
                "process of the HIT. Go back to the HIT by closing this warning " +
                "window.\nSorry that we prevent you from leaving as long as " +
                "you have this page open." +
                "If you want to go to other tabs or programs," +
                "please simply close the tab.";
            if (!confirm(leave_message)) {
                if (!document.hasFocus()) {
                    console.log("user left the page");
                    $("#submit_answer").disable();
                }
            }
        }
    });
});