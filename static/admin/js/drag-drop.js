document.addEventListener('DOMContentLoaded', function() {
    const dragDropUploads = document.querySelectorAll('.drag-drop-upload');
    
    dragDropUploads.forEach(function(container) {
        const fileInput = container.querySelector('input[type="file"]');
        const uploadText = document.createElement('div');
        uploadText.className = 'upload-text';
        uploadText.innerHTML = `
            <div class="upload-icon">📁</div>
            <div class="text-default">${container.dataset.defaultText || '点击选择文件或拖拽文件到这里'}</div>
            <div class="text-hover" style="display: none;">${container.dataset.hoverText || '松开鼠标上传文件'}</div>
        `;
        container.appendChild(uploadText);
        
        const textDefault = uploadText.querySelector('.text-default');
        const textHover = uploadText.querySelector('.text-hover');
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        container.appendChild(fileName);
        
        // 点击事件
        container.addEventListener('click', function() {
            fileInput.click();
        });
        
        // 拖拽事件
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            container.classList.add('drag-over');
            textDefault.style.display = 'none';
            textHover.style.display = 'block';
        });
        
        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            container.classList.remove('drag-over');
            textDefault.style.display = 'block';
            textHover.style.display = 'none';
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            container.classList.remove('drag-over');
            textDefault.style.display = 'block';
            textHover.style.display = 'none';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileName(e.dataTransfer.files[0].name);
            }
        });
        
        // 文件选择事件
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length) {
                updateFileName(fileInput.files[0].name);
            }
        });
        
        function updateFileName(name) {
            fileName.textContent = '已选择文件: ' + name;
        }
    });
});