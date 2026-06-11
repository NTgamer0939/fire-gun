$(document).ready(function() {
    const socket = io("http://localhost:3000");
    let state = "logs";
    let currentPage = 1;

    socket.on('connect', () => {
        console.log("Connected to server");
    });

    socket.on("connect_error", (err) => {
        console.log("Lỗi kết nối:", err);
    });

    // Toggle between logs mode and stream mode
    $('#change_mode').on('click', function() {
        if (state === "logs") {
            state = "stream";
            socket.emit('join_stream');
            $('#show_content').removeClass('logs');
            $('#show_content').addClass('stream_video');
            $('#show_content').html('');
            $('#show_content').html(`<img id="img-stream" src="" alt="Stream">`);
            $('#show_content').attr('width', '640px');
            $('#show_content').attr('height', '480px');
            $('#title-log-div > p').text('Hình ảnh trực tiếp');
            $('#change_mode').text('Xem nhật ký');
            $('#pagination').hide();
            console.log('join');
        } else {
            state = "logs";
            socket.emit('leave_stream');
            $('#show_content').removeClass('stream_video');
            $('#show_content').addClass('logs');
            $('#show_content').attr('width', 'auto');
            $('#show_content').attr('height', 'auto');
            $('#title-log-div > p').text('Nhật ký báo cháy');
            $('#change_mode').text('Xem trực tiếp');
            $('#pagination').show();
            console.log('leave');
        }
    });


    socket.on('new_log', (data) => {
        loadLogs(data);
    });

    // Streaming
    let busy = false;
    let lastedFrame = null;
    let lastUrl = null;

    function renderFrame(frame) {
        busy = true;
        const blob = new Blob([frame], {type: 'image/jpeg'});
        const url = URL.createObjectURL(blob);

        if (lastUrl) {
            URL.revokeObjectURL(lastUrl);
        }

        $('#img-stream').attr('src', url);
        lastUrl = url;
        busy = false;
    }
    
    socket.on('stream', (data) => {
        if (busy) {
            console.log('new');
            lastedFrame = data;
            return;
        }
        renderFrame(data);
    });

    // Pagination
    $('.direction_button').on('click', function() {
        const direction = $(this).data('direction');
        if (direction == -1 && currentPage == 1) {
            return;
        }
        currentPage += direction;
        $('#page_numbers').text(currentPage);
        $.ajax({
            url: '/change_page',
            method: 'POST',
            dataType: 'json',
            data: {
                page: currentPage
            },
            success: (res) => {
                loadLogs(res);
            }
        });
    });

    // Export logs
    $('#export_button').on('click', function(){
        $.ajax({
            url: '/export',
            method: 'POST',
            success: function(response) {
                downloadFile(response);
            }
        });
    });

    // Load new logs
    function loadLogs(data) {
        if ($('#show_content').hasClass('stream_video')) return;
        console.log("Loading logs...");
        $('#show_content').html('');
        for (i = 0; i < data.length; i++) {
            console.log(data.length);
            $('#show_content').append(`
                <ul class="log">
                    <li class="content">🔥 Detected fire in: </li>
                    <li class="date">${data[i].datetime}</li></ul>
                    <li class="image">
                        <img src="${window.location.origin}/${data[i].imagePath}" alt="Log image">
                    </li>
                </ul>
            `);
        }
        console.log("Loaded logs");
    }

    // Download logs
    function downloadFile(data) {
        const blob = new Blob([data], { type: 'text' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "Fire_gun's logs.txt";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

});