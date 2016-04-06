/**
 * Created by moonkey on 4/1/16.
 */

$(document).ready(function () {
    var male_info = $('#male_info');
    var female_info = $('#female_info');
    var neutral_info = $('#neutral_info');
    var error_info = $('#error_info');
    var noname_info = $('#noname_info');
    var report_info = $('#report_confirm');
    var country_info = $('#country_result');

    function hide_all_info() {
        male_info.hide();
        female_info.hide();
        neutral_info.hide();

        error_info.hide();
        noname_info.hide();
        report_info.hide();
        country_info.hide();
    }

    var name_form = $('#name_form');
    name_form.submit(function (e) {
        e.preventDefault();
        var form_data = $(this).serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }

        $.ajax({
            url: this.action,
            type: "POST",
            cache: false,
            async: true,
            traditional: true,
            data: form_dict,
            dataType: 'json',
            success: function (response) {
//                GENDER
                hide_all_info();
                if (response['gender'] == 'MALE') {
                    male_info.fadeIn();
                }
                else if (response['gender'] == 'FEMALE') {
                    female_info.fadeIn();
                }
                else if (response['gender'] == 'LOVELY') {
                    neutral_info.fadeIn();
                    $('#lpic').hidden();
                    $('#footer').html(
                        'It has been a nice day. :) <br>--<font color="white">Moonkey</font>');
                }
                else if (response['gender'] == 'NONAME') {
                    noname_info.fadeIn();
                }
                else if (response['gender'] == 'SPECIAL') {
                    window.location.replace(response['redirect_url']);
                }
//                COUNTRY
                country_info.fadeIn();
                $('#country_predicted').html(response['country']);
            },
            error: function (xhr) {
                hide_all_info();
                error_info.fadeIn();
            }
        });
    });

    var report_male = $('#report_male');
    var report_female = $('#report_female');
    var input_name = $('#name');
    report_female.click(function (e) {
        report(false);
    });
    report_male.click(function (e) {
        report(true);
    });
    function report(male) {
        var current_name = input_name.val();
        $.ajax({
            url: '/nameall/name_report',
            type: "POST",
            cache: false,
            async: true,
            traditional: true,
            data: {'name': current_name, 'gender': male},
            dataType: 'json',
            success: function (response) {
                hide_all_info();
                report_info.fadeIn();
            },
            error: function (xhr) {
                hide_all_info();
                error_info.fadeIn();
            }
        });
    }
});