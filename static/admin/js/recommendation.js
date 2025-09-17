(function($) {
    $(document).ready(function() {
        // 为推荐歌曲选择器添加搜索功能
        function initRecommendationSearch() {
            // 获取选择器元素
            const $select = $('#id_recommended_songs_from, #id_recommended_songs_to');
            const $fromSelect = $('#id_recommended_songs_from');
            const $toSelect = $('#id_recommended_songs_to');
            
            // 为左侧选择器添加搜索框
            if ($fromSelect.length && $fromSelect.siblings('.recommendation-search').length === 0) {
                const searchInput = $('<input type="text" placeholder="搜索歌曲..." class="recommendation-search">');
                $fromSelect.before(searchInput);
                
                // 添加搜索功能
                searchInput.on('keyup', function() {
                    const searchTerm = $(this).val().toLowerCase();
                    $fromSelect.find('option').each(function() {
                        const text = $(this).text().toLowerCase();
                        if (text.indexOf(searchTerm) > -1) {
                            $(this).show();
                        } else {
                            $(this).hide();
                        }
                    });
                });
            }
        }
        
        // 初始化搜索功能
        initRecommendationSearch();
        
        // 监听DOM变化，确保动态加载的内容也能有搜索功能
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    initRecommendationSearch();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
})(django.jQuery);