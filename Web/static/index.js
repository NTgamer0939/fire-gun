$(document).ready(function() {
    const socket = io("http://localhost:3000");
    let state = "logs";
    let currentPage = 1;
    let timeAutoRefresh;
    let viewWidth = innerWidth;
    let camera = false;

    socket.on('connect', () => {
        console.log("Connected to server");
    });

    socket.on("connect_error", (err) => {
        console.log("Lỗi kết nối:", err);
    });

    // Auto refresh page if window resize < or > 768px
    $(window).resize(function(){
        if (parseInt(1 + (innerWidth - 768) / (innerWidth * -1 - 768)) != parseInt(1 + (viewWidth - 768) / (viewWidth * -1 - 768))) window.location.reload();
    })

    // Spin warning
    if (viewWidth <= 768) $('#alert-warning-spin-device').show()
    else $('#alert-warning-spin-device').remove();
    $('#alert-warning-spin-device').click(function(){
        $('#alert-warning-spin-device').remove();
    })

    // Animation code and toggle between logs mode and stream mode
    $('#block').click(function() {
        let logSlideIn = '';
        let logSlideOut = '';
        let streamSlideIn = '';
        let streamSlideOut = '';

        let logMode = '';
        let streamMode = '';

        let defaultDirectionAnimation = '';

        let delayMode = 0;

        if (viewWidth > 768) {
            logSlideIn = 'slideTopIn 500ms 600ms forwards';
            logSlideOut = 'slideTopOut 500ms forwards';
            streamSlideIn = 'slideBottomIn 500ms 700ms forwards';
            streamSlideOut = 'slideBottomOut 500ms forwards';

            logMode = 'changeLogMode';
            streamMode = 'changeStreamMode';

            defaultDirectionAnimation = 'bottom';

            delayMode = 0;
        }
        else {
            logSlideIn = 'slideLeftInContent 500ms 600ms forwards';
            logSlideOut = 'slideRightOutContent 500ms forwards';
            streamSlideIn = 'slideRightInContent 600ms 570ms forwards';
            streamSlideOut = 'slideLeftOutContent 500ms forwards';

            logMode = 'changeLogModeMobile';
            streamMode = 'changeStreamModeMobile';

            defaultDirectionAnimation = 'right';

            delayMode = 500;
        }

        if ($('#block').hasClass('logBlock')){
            // Log mode
            socket.emit('leave_stream');

            $('#block').addClass('streamBlock');
            $('#block').removeClass('logBlock');
            
            $('#content-log').show();
            $('#content-log').css('opacity', '0');
            $('#content-log').css('animation-delay', '300ms');
            $('#content-log').css('animation-name', 'slideLeftInContent');
            $('#content-stream').css('animation-delay', '0ms');
            $('#content-stream').css('animation-name', 'slideRightOutContent');
            
            $('#block').css(defaultDirectionAnimation, 'auto');
            $('#block').css('animation-name', logMode);
            
            $('#nav-log-main > *').css('animation', logSlideIn);
            $('#nav-stream-main > *').css('animation', streamSlideOut);
            setTimeout(lambda => $('#nav-log-main').css('z-index', '1'), delayMode);
            setTimeout(lambda => $('#nav-stream-main').css('z-index', '0'), delayMode);
            
            $('body > *').removeClass('blur')
        } else {
            // Stream mode
            socket.emit('join_stream');

            $('#block').addClass('logBlock');
            $('#block').removeClass('streamBlock');
            
            $('#content-log').css('animation-delay', '0ms');
            $('#content-log').css('animation-name', 'slideLeftOutContent');
            $('#content-stream').css('animation-delay', '300ms');
            $('#content-stream').css('animation-name', 'slideRightInContent');
            
            $('#block').css(defaultDirectionAnimation, '0');
            $('#block').css('animation-name', streamMode);
            
            $('#nav-log-main > *').css('animation', logSlideOut);
            $('#nav-stream-main > *').css('animation', streamSlideIn);
            setTimeout(lambda => $('#nav-log-main').css('z-index', '0'), delayMode);
            setTimeout(lambda => $('#nav-stream-main').css('z-index', '1'), delayMode);

            $('body > *').addClass('blur');
            $('#nav-stream-main, content-stream > *, #block').removeClass('blur');

            setTimeout(lambla => $('#content-log').hide(), 500 );
            $('#content-stream').css('opacity', '0');
        }
    })

    socket.on('new_log', (data) => {
        loadLogs(data);
    });

    socket.on('camera_status', (data) => {
        camera = (data) ? true : false;

        if (camera) return;

        $('#content-stream').text('Camera đang không hoạt động vào lúc này!');
        console.log('afagsggassadg')
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
    $('.direction-button').on('click', function() {
        const direction = $(this).data('direction');
        if (direction == -1 && currentPage == 1) {
            return;
        }
        currentPage += direction;
        $('#page-numbers').text(currentPage);
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
    $('#export-button').on('click', function(){
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
        if ($('#block').hasClass('logBlock')) return;
        console.log("Loading logs...");
        $('#content-log').html('');
        for (i = 0; i < data.length; i++) {

            let returnVal = attachFlag(data[i].datetime);
            let flag = returnVal.flag;
            if (flag == 'red') timeAutoRefresh = returnVal.time;
            $('#content-log').append(`
                <ul class="log">
                    <li class="content">🔥 Phát hiện đám cháy vào lúc: </li>
                    <li class="date"> ${data[i].datetime}</li>
                    <li class="flag ${flag}"></li>
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
        if ($('#block').hasClass('streamBlock')) return;
        const date = new Date();

        const second = date.getSeconds();
        const minute = date.getMinutes();
        const hour = date.getHours();
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();

        const time = `🕑 ${day}/${month}/${year} ${hour}:${minute}:${second}`;

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