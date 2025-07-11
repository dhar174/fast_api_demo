// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const classifyBtn = document.getElementById('classifyBtn');
const imageResult = document.getElementById('imageResult');
const textInput = document.getElementById('textInput');
const sentimentBtn = document.getElementById('sentimentBtn');
const sentimentResult = document.getElementById('sentimentResult');
const loadingOverlay = document.getElementById('loadingOverlay');
const statusCard = document.getElementById('statusCard');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
    setupEventListeners();
});

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            statusIndicator.className = 'status-indicator online';
            statusText.textContent = 'Server Online';
        } else {
            throw new Error('Server responded with error');
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator offline';
        statusText.textContent = 'Server Offline';
        console.error('Server status check failed:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input change
    imageInput.addEventListener('change', handleFileSelect);
    
    // Classify button
    classifyBtn.addEventListener('click', classifyImage);
    
    // Sentiment analysis button
    sentimentBtn.addEventListener('click', analyzeSentiment);
    
    // Enter key for sentiment analysis
    textInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            analyzeSentiment();
        }
    });
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File selection handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Handle file processing
function handleFile(file) {
    // Validate file type
    if (!file.type.match(/image\/(jpeg|png)/)) {
        showNotification('Please select a JPEG or PNG image.', 'error');
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File size must be less than 10MB.', 'error');
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImg.src = e.target.result;
        imagePreview.style.display = 'block';
        imageResult.style.display = 'none';
        uploadArea.style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // Store file for classification
    imageInput.file = file;
}

// Classify image
async function classifyImage() {
    const file = imageInput.file;
    if (!file) {
        showNotification('Please select an image first.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayImageResult(result);
        
    } catch (error) {
        console.error('Classification error:', error);
        showNotification('Classification failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Display image classification result
function displayImageResult(result) {
    document.getElementById('predictedClass').textContent = result.predicted_class.replace(/_/g, ' ');
    document.getElementById('confidence').textContent = `${(result.confidence * 100).toFixed(2)}%`;
    
    // Update confidence bar
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceFill.style.width = `${result.confidence * 100}%`;
    
    // Show result
    imageResult.style.display = 'block';
    imageResult.scrollIntoView({ behavior: 'smooth' });
}

// Analyze sentiment
async function analyzeSentiment() {
    const text = textInput.value.trim();
    if (!text) {
        showNotification('Please enter some text to analyze.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/sentiment_analysis?text=${encodeURIComponent(text)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displaySentimentResult(result);
        
    } catch (error) {
        console.error('Sentiment analysis error:', error);
        showNotification('Sentiment analysis failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Display sentiment analysis result
function displaySentimentResult(result) {
    const sentiment = result.sentiment;
    const sentimentLabel = document.getElementById('sentimentLabel');
    const sentimentScore = document.getElementById('sentimentScore');
    const scoreFill = document.getElementById('scoreFill');
    
    // Update sentiment label
    sentimentLabel.textContent = sentiment.label.toUpperCase();
    sentimentLabel.className = `value sentiment-badge ${sentiment.label.toLowerCase()}`;
    
    // Update score
    sentimentScore.textContent = sentiment.score.toFixed(4);
    
    // Update score bar
    scoreFill.style.width = `${sentiment.score * 100}%`;
    
    // Show result
    sentimentResult.style.display = 'block';
    sentimentResult.scrollIntoView({ behavior: 'smooth' });
}

// Show/hide loading overlay
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles for notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    
    // Add notification to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Reset image upload
function resetImageUpload() {
    imageInput.value = '';
    imageInput.file = null;
    imagePreview.style.display = 'none';
    imageResult.style.display = 'none';
    uploadArea.style.display = 'block';
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
`;
document.head.appendChild(style);

// Add reset button functionality
document.addEventListener('click', function(e) {
    if (e.target.closest('.upload-area') && imagePreview.style.display === 'block') {
        if (confirm('Reset image upload?')) {
            resetImageUpload();
        }
    }
});
