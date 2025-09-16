document.addEventListener('DOMContentLoaded', function () {
    // 为所有切换按钮添加点击事件
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('toggle-records')) {
            const songId = e.target.getAttribute('data-song-id');
            const recordsContent = document.getElementById('records-' + songId);

            if (recordsContent) {
                if (recordsContent.style.display === 'none' || recordsContent.style.display === '') {
                    // 展开记录
                    recordsContent.style.display = 'block';
                    recordsContent.classList.add('show');
                    recordsContent.classList.remove('hide');
                    e.target.textContent = '收起记录';
                } else {
                    // 收起记录
                    recordsContent.style.display = 'none';
                    recordsContent.classList.add('hide');
                    recordsContent.classList.remove('show');
                    e.target.textContent = '查看记录';
                }
            }
        }
    });
}); 