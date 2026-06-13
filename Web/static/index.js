$(document).ready(function() {
    const socket = io("http://localhost:3000");
    let state = "logs";
    let currentPage = 1;
    let timeAutoRefresh;

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
            $('#show_content').append(`<img id="img-stream" src="" alt="Stream">`);
            $('#show_content').append('<span id="clock"></span>');
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
            $('#show_content').html('');
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
        let flag;
        if ($('#show_content').hasClass('stream_video')) return;
        console.log("Loading logs...");
        $('#show_content').html('');
        for (i = 0; i < data.length; i++) {

            let returnVal = attachFlag(data[i].datetime);
            let flag = returnVal.flag;
            if (flag == 'red') timeAutoRefresh = returnVal.time;
            $('#show_content').append(`
                <ul class="log">
                    <li class="content">🔥 Detected fire in: </li>
                    <li class="date">${data[i].datetime}</li>
                    <li class="flag ${flag}"></li></ul>
                    <li class="image">
                        <img src="${window.location.origin}/${data[i].imagePath}" alt="Log image">
                    </li>
                </ul>
            `);
        }

        if (timeAutoRefresh) setTimeout(autoRefresh, (30 - timeAutoRefresh + 1) * 1000 * 60);

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

    // Clock
    function clockRun() {
        if (state != "stream") return;
        const date = new Date();

        const second = date.getSeconds();
        const minute = date.getMinutes();
        const hour = date.getHours();
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();

        const time = `🕑${day}/${month}/${year} ${hour}:${minute}:${second}`;

        $('#clock').text(time);
    }

    // Attach flag for every warning
    function attachFlag(s2) {
        const defaultTime = 30;
        const nowDate = new Date();

        const second = String(nowDate.getSeconds()).padStart(2, '0');
        const minute = String(nowDate.getMinutes()).padStart(2, '0');
        const hour = String(nowDate.getHours()).padStart(2, '0');
        const day = String(nowDate.getDate()).padStart(2, '0');
        const month = String(nowDate.getMonth() + 1).padStart(2, '0');
        const year = String(nowDate.getFullYear());

        const s1 = `${day}/${month}/${year} ${hour}:${minute}:${second}`;
        console.log(s1);

        const dates1 = s1.split(' ');
        const dates2 = s2.split(' ');

        const times1 = dates1[1].split(':');
        const times2 = dates2[1].split(':');

        const cTimes1 = parseInt(times1[0] + times1[1] + times1[2]);
        const cHours1 = parseInt(times1[0]);
        const cHours2 = parseInt(times2[0]);
        const cMinutes1 = parseInt(times1[1]);
        const cMinutes2 = parseInt(times2[1]);

        const days1 = dates1[0].split('/');
        const days2 = dates2[0].split('/');

        const cDays1 = parseInt(days1[2] + days1[1] + days1[0]);
        let cDays2Tmp = parseInt(days2[2].padStart(2, '0') + days2[1].padStart(2, '0') + days2[0].padStart(2, '0'));
        if (cTimes1 < 1500) cDays2Tmp++;
        const cDays2 = cDays2Tmp;

        if (cDays1 == cDays2) {
            if ((cHours1 == cHours2) && (cMinutes1 - cMinutes2 < defaultTime)) return {flag: 'red', time: cMinutes1 - cMinutes2};
            if ((cHours1 - cHours2 == 1) && ((60 - cMinutes2) + cMinutes1 <= defaultTime)) return {flag: 'red', time: (60 - cMinutes2) + cMinutes1};
        }
        return {flag: 'green', time: -1};
    }

    function autoRefresh() {
        if ($('.flag').hasClass('red')) window.location.reload();
    }

    setInterval(clockRun, 1000);
});