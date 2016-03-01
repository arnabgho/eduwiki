/**
 * Created by moonkey on 2/29/16.
 */

$(document).ready(function () {
    var pixel_size = 20;
    var pos_x, pos_y, timeout;//, totimes = 100, distance = 30;
    var trajectory = [];
    var actions = [];
    var steps = 0;

    var canvas = document.getElementById("cas"), ctx = canvas.getContext("2d");
    var canvasBox = document.getElementById("bb");
    canvas.width = canvasBox.clientWidth;
    canvas.height = canvasBox.clientHeight;
    mask_img.onload = function () {
        var w = canvas.height * mask_img.width / mask_img.height;
        ctx.drawImage(mask_img, (canvas.width - w) / 2, 0, w, canvas.height);
//        tapClip();
        startOrigin();
    };

    var label_form = $('#label_form');
    label_form.submit(function (e) {
        e.preventDefault();
        var form_data = $(this).serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }
        form_dict['trajectory'] = JSON.stringify(trajectory);
        form_dict['actions'] = JSON.stringify(actions);
        info_region = $('#submit_info');
        $.ajax({
            url: this.action,
            type: "POST",
            cache: false,
            async: true,
            traditional: true,
            data: form_dict,
            dataType: 'json',
            success: function (response) {
                // Nothing needs to be done for the intermediate results
                $(window).scrollTop(next_pos);
                info_region.html('<b>Label successfully submitted to server.</b>');
                info_region.addClass('alert-success');
                info_region.removeClass('alert-danger');
                info_region.show();
            },
            error: function (xhr) {
                info_region.html(
                        "<b>Error: The label was not successfully submitted." +
                        "Please report to the webmaster.</b>");
                info_region.addClass('alert-danger');
                info_region.removeClass('alert-success');
                info_region.show();
                $('#error_info').html(xhr.responseText);
            }
        });
    });

    function getClipArea(e, hastouch) {
        var x = hastouch ? e.targetTouches[0].pageX : e.clientX;
        var y = hastouch ? e.targetTouches[0].pageY : e.clientY;
        var ndom = canvas;
        while (ndom.tagName !== "BODY") {
            x -= ndom.offsetLeft;
            y -= ndom.offsetTop;
            ndom = ndom.parentNode;
        }
        return {
            x: x,
            y: y
        }
    }

    function startOrigin() {
        // Getting the erasing effect by changing "globalCompositeOperation"
        ctx.globalCompositeOperation = "destination-out";
        clearTimeout(timeout);

        var keydown = "keydown";
        pos_x = 0;
        pos_y = 0;
        goDot(pos_x, pos_y);
        window.addEventListener(keydown, keydownHandler);
    }

    function keydownHandler(e) {
        e = e || event;
        var next_x, next_y;
        //window.alert(e.keyCode);
//        if (e.keyCode == "81") {
//            // Q
//            next_x = pos_x - pixel_size;
//            next_y = pos_y - pixel_size;
//            goDot(next_x, next_y);
//        }
//        if (e.keyCode == "69") {
//            // E
//            next_x = pos_x + pixel_size;
//            next_y = pos_y - pixel_size;
//            goDot(next_x, next_y);
//        }
//        if (e.keyCode == "90") {
//            // E
//            next_x = pos_x - pixel_size;
//            next_y = pos_y + pixel_size;
//            goDot(next_x, next_y);
//        }
//        if (e.keyCode == "67") {
//            // C
//            next_x = pos_x + pixel_size;
//            next_y = pos_y + pixel_size;
//            goDot(next_x, next_y);
//        }
        if (e.keyCode == "37" || e.keyCode == "65") {
            // left
            next_x = pos_x - pixel_size;
            goDot(next_x, pos_y);
        }
        if (e.keyCode == "38" || e.keyCode == "87") {
            // up or W
            next_y = pos_y - pixel_size;
            goDot(pos_x, next_y);
        }
        if (e.keyCode == "39" || e.keyCode == "68") {
            // right or D
            next_x = pos_x + pixel_size;
            goDot(next_x, pos_y);
        }
        if (e.keyCode == "40" || e.keyCode == "88") {
            // down or W
            next_y = pos_y + pixel_size;
            goDot(pos_x, next_y);
        }
    }

    function goDot(next_x, next_y) {
        next_x = Math.min(Math.max(next_x, 0), canvas.width - pixel_size);
        next_y = Math.min(Math.max(next_y, 0), canvas.height - pixel_size);

        if (pos_x > next_x) {
            actions.push(0);
        }
        if (pos_x < next_x) {
            actions.push(1);
        }
        if (pos_y > next_y) {
            actions.push(2);
        }
        if (pos_y < next_y) {
            actions.push(3);
        }
        pos_x = next_x;
        pos_y = next_y;
        drawDot(pos_x, pos_y);

        trajectory.push([pos_x / pixel_size, pos_y / pixel_size]);
        steps = trajectory.length;

        document.getElementById("steps").innerHTML = steps.toString();
    }

    function drawDot(x1, y1) {
        ctx.save();
        ctx.beginPath();
        ctx.rect(x1, y1, pixel_size, pixel_size);
        ctx.fill();
        ctx.restore();
    }

//    function tapClip() {
//        var hastouch = false, tapstart = "mousedown", keydown = "keydown";
//        var area;
//        ctx.globalCompositeOperation = "destination-out";
//
//        function tapstartHandler(e) {
//            clearTimeout(timeout);
//            e.preventDefault();
//            area = getClipArea(e, hastouch);
//            var x = Math.round(area.x / pixel_size) * pixel_size;
//            var y = Math.round(area.y / pixel_size) * pixel_size;
//            x = Math.max(x, 10);
//            y = Math.max(y, 10);
//            x = Math.min(x, canvas.width - 10);
//            y = Math.min(y, canvas.height - 10);
//            goDot(x, y);
//            this.removeEventListener(tapstart, tapstartHandler);
//            this.addEventListener(keydown, keydownHandler);
//        }
//
//        window.addEventListener(tapstart, tapstartHandler);
//    }
});