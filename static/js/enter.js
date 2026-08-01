$(document).ready(function() {
    var FACES = ['top', 'bottom', 'front', 'back', 'left', 'right'];
    var COLOR_NAMES = ['white', 'yellow', 'red', 'orange', 'blue', 'green'];
    var currentColors = {};
    var detectedCount = 0;

    FACES.forEach(function(face) {
        currentColors[face] = [];
        for (var i = 0; i < 9; i++) {
            currentColors[face].push('white');
        }
    });

    FACES.forEach(function(face) {
        var grid = $('#grid-' + face);
        grid.find('.color-cell').each(function() {
            var cell = $(this);
            cell.on('click', function() {
                var cur = cell.attr('data-color');
                var curIdx = COLOR_NAMES.indexOf(cur);
                var next = COLOR_NAMES[(curIdx + 1) % COLOR_NAMES.length];
                cell.removeClass(cur).addClass(next).attr('data-color', next);
                var idx = parseInt(cell.attr('data-index'));
                currentColors[face][idx] = next;
            });
        });
    });

    function setGridColors(face, colors) {
        currentColors[face] = colors.slice();
        var grid = $('#grid-' + face);
        grid.find('.color-cell').each(function(idx) {
            var cell = $(this);
            var color = colors[idx];
            COLOR_NAMES.forEach(function(c) { cell.removeClass(c); });
            cell.addClass(color).attr('data-color', color);
        });
    }

    function updateProgress() {
        detectedCount = 0;
        FACES.forEach(function(face) {
            var badge = $('#status-' + face);
            if (badge.hasClass('bg-success')) {
                detectedCount++;
            }
        });
        if (detectedCount > 0 && detectedCount < 6) {
            $('#detect-progress').removeClass('d-none');
            $('#detect-progress-text').text('Detected: ' + detectedCount + '/6 faces');
        } else if (detectedCount === 6) {
            $('#detect-progress').removeClass('d-none');
            $('#detect-progress-text').text('All 6 faces detected! Ready to solve.');
        } else {
            $('#detect-progress').addClass('d-none');
        }
    }

    FACES.forEach(function(face) {
        var fileInput = $('#file-input-' + face);
        var uploadBtn = $('.upload-btn[data-face="' + face + '"]');

        uploadBtn.on('click', function() {
            fileInput.trigger('click');
        });

        fileInput.on('change', function(e) {
            var file = e.target.files[0];
            if (!file) return;

            var badge = $('#status-' + face);
            var originalHtml = uploadBtn.html();
            badge.removeClass('bg-success bg-danger').addClass('bg-secondary').text('...');
            uploadBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span>Detecting...');

            var reader = new FileReader();
            reader.onload = function(ev) {
                var imageData = ev.target.result;

                fetch('/detect-face/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ face: face, image: imageData })
                })
                .then(function(resp) { return resp.json(); })
                .then(function(data) {
                    uploadBtn.prop('disabled', false).html('<i class="fas fa-camera me-1"></i>Upload Image');
                    if (data.error) {
                        badge.removeClass('bg-secondary').addClass('bg-danger').text('Error');
                        $('#error-alert').text(face + ': ' + data.error).removeClass('d-none');
                        return;
                    }
                    var colors = data.colors[face];
                    if (colors) {
                        setGridColors(face, colors);
                        badge.removeClass('bg-secondary bg-danger').addClass('bg-success').text('Done');
                    }
                    updateProgress();
                })
                .catch(function(err) {
                    uploadBtn.prop('disabled', false).html('<i class="fas fa-camera me-1"></i>Upload Image');
                    badge.removeClass('bg-secondary').addClass('bg-danger').text('Error');
                    $('#error-alert').text(face + ' detection failed: ' + err.message).removeClass('d-none');
                    updateProgress();
                });
            };
            reader.readAsDataURL(file);
            fileInput.val('');
        });
    });

    $('#solve-btn').on('click', function() {
        $('#error-alert').addClass('d-none');
        $('#loading').removeClass('d-none');
        $('#solve-btn').prop('disabled', true);

        fetch('/solve/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ colors: currentColors })
        })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            if (data.error) {
                $('#error-alert').text(data.error).removeClass('d-none');
                $('#loading').addClass('d-none');
                $('#solve-btn').prop('disabled', false);
                return;
            }
            window.location.href = '/solve-page/';
        })
        .catch(function(err) {
            $('#error-alert').text('Request failed: ' + err.message).removeClass('d-none');
            $('#loading').addClass('d-none');
            $('#solve-btn').prop('disabled', false);
        });
    });

    $('#reset-btn').on('click', function() {
        FACES.forEach(function(face) {
            var whiteColors = [];
            for (var i = 0; i < 9; i++) { whiteColors.push('white'); }
            setGridColors(face, whiteColors);
            var badge = $('#status-' + face);
            badge.removeClass('bg-success bg-danger bg-secondary').text('');
        });
        detectedCount = 0;
        $('#detect-progress').addClass('d-none');
        $('#error-alert').addClass('d-none');
        $('#loading').addClass('d-none');
        $('#solve-btn').prop('disabled', false);
    });
});
