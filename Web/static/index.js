$(document).ready(function() {
    const socket = io({
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        transports: ['polling'],
        withCredentials: true
    });
    var state = "logs";
    var currentPage = 1;
    var clientId;

    console.log(socket);
    socket.on('connect', () => {
        console.log("Connected to server");
    });

    socket.on('getID', (data) => {
        clientId = data;
        console.log(clientId);
    });
    
    socket.on("connect_error", (err) => {
        console.log("Lỗi kết nối:", err);
    });

    // Toggle between logs mode and stream mode
    $('#change_mode').on('click', function() {
        if (state === "logs") {
            state = "stream";
            $.ajax({
                url: '/start_stream',
                method: 'POST',
                data: {
                    clientID: clientId
                }
            });
            
            $('#show_content').removeClass('logs');
            $('#show_content').addClass('stream_video');
            $('#show_content').html('');
            $('#show_content').html(`<img id="img-stream" src="" alt="Stream">`);
            $('#show_content').attr('width', '640px');
            $('#show_content').attr('height', '480px');
            $('#title-log-div > p').text('Hình ảnh trực tiếp');
            $('#change_mode').text('Xem nhật ký');
            $('#pagination').hide();
            
        } else {
            state = "logs";
            $.ajax({
                url: '/stop_stream',
                method: 'POST',
                data: {
                    clientID: clientId
                }
            });

            $('#show_content').removeClass('stream_video');
            $('#show_content').addClass('logs');
            $('#show_content').attr('width', 'auto');
            $('#show_content').attr('height', 'auto');
            $('#title-log-div > p').text('Nhật ký báo cháy');
            $('#change_mode').text('Xem trực tiếp');
            $('#pagination').show();
        }
    });


    socket.on('new_log', (data) => {
        if ($('#show_content').hasClass('stream_video')) {
            return;
        }
        loadLogs(data);
    });

    // Streaming
    var busy = false;
    var lastedFrame = null;

    function renderFrame(frame) {
        busy = true;
        $('#img-stream').attr('src', `data:image/jpeg;base64,${frame}`);
        busy = false;
    }
    
    socket.on('stream_frame', (data) => {
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
            data: {
                page: currentPage,
                clientID: clientId
            }
        });
    });

    // Export logs
    $('#export_button').on('click', function(){
        $.ajax({
            url: '/export',
            method: 'POST',
            data: {
                clientID: clientId
            },
            success: function(response) {
                downloadFile(response);
            }
        });
    });

    // Load new logs
    function loadLogs(data) {
        console.log("Loading logs...");
        $('#show_content').html('');
        for (let i = 0; i < data.length; i++) {
            console.log(data.length);
            $('#show_content').append(`
                <ul class="log">
                    <li class="content">🔥 Detected fire in: </li>
                    <li class="date">${data[i].datetime}</li></ul>
                    <li class="image">
                        <img src="data:image/jpeg;base64,${data[i].image}" alt="Log Image">
                    </li>
                </ul>
            `);
        }
        console.log("Logs loaded");
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