/**
 * Created by moonkey on 6/19/15.
 */

$(document).ready(function () {
    var topic_confidence_bar = $('#topic_confidence');
    var after_topic_confidence = $('#after_topic_confidence');
    var pre_topic_confidence = $('#pre_topic_confidence');

    topic_confidence_bar.change(function (e) {
        if (this.value <= 0) {
            return 1;
        }

        after_topic_confidence.show();
        pre_topic_confidence.hide();
//        this.attr("readonly", true);
    });
});