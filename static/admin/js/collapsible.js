// 演唱记录折叠/展开功能 - 使用原生JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('Collapsible script loaded');
    
    // 为所有切换按钮添加点击事件
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('toggle-records')) {
            const songId = e.target.getAttribute('data-song-id');
            const recordsContent = document.getElementById('records-' + songId);
            
            console.log('Toggle button clicked, song_id:', songId);
            
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
            } else {
                console.error('Content not found for song_id:', songId);
            }
        }
    });
    
    console.log('Collapsible event handlers registered');
});
