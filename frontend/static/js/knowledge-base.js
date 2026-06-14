// Knowledge Base page functionality

async function loadKnowledgeBase() {
    setActiveNav('nav-kb');
    document.getElementById('page-title').textContent = 'Knowledge Base Management';
    showLoading(true);

    try {
        const articles = await apiCall('/articles?limit=20&offset=0');

        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">
                    <i class="bi bi-cloud-upload"></i> Upload Article
                </div>
                <div class="card-body">
                    <form id="upload-form">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" id="article-title" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Tags</label>
                                <input type="text" class="form-control" id="article-tags" placeholder="comma,separated">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" id="article-description" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Article File</label>
                            <div class="file-upload-area" id="file-upload-area">
                                <i class="bi bi-cloud-upload"></i>
                                <p>Drag and drop your file here or click to select</p>
                                <small class="text-muted">Supported formats: .md, .txt</small>
                                <input type="file" id="article-file" accept=".md,.txt" style="display: none;">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-upload"></i> Upload Article
                        </button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-list"></i> Articles</span>
                    <input type="text" class="form-control" id="search-articles" placeholder="Search..." style="width: 200px;">
                </div>
                <div class="card-body">
                    <div id="articles-table-container">
                        ${renderArticlesTable(articles)}
                    </div>
                </div>
            </div>
        `;

        // Setup file upload
        setupFileUpload();
        setupArticleSearch();
        setupUploadForm();

    } catch (error) {
        console.error('Error loading knowledge base:', error);
        showAlert('Failed to load knowledge base', 'danger');
    }
}

function setupFileUpload() {
    const uploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('article-file');

    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
        updateFileLabel();
    });

    fileInput.addEventListener('change', updateFileLabel);
}

function updateFileLabel() {
    const fileInput = document.getElementById('article-file');
    if (fileInput.files.length > 0) {
        document.getElementById('file-upload-area').innerHTML = `
            <i class="bi bi-check-circle text-success"></i>
            <p><strong>${fileInput.files[0].name}</strong></p>
        `;
    }
}

async function setupUploadForm() {
    document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('article-title').value;
        const description = document.getElementById('article-description').value;
        const tags = document.getElementById('article-tags').value;
        const file = document.getElementById('article-file').files[0];

        if (!title || !file) {
            showAlert('Please fill in all required fields', 'warning');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            formData.append('tags', tags);
            formData.append('file', file);

            const response = await fetch('/api/articles/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            showAlert('Article uploaded successfully', 'success');
            document.getElementById('upload-form').reset();
            updateFileLabel();
            loadKnowledgeBase();

        } catch (error) {
            showAlert('Failed to upload article: ' + error.message, 'danger');
        }
    });
}

function setupArticleSearch() {
    let searchTimeout;
    document.getElementById('search-articles').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const query = e.target.value;
            if (query.length > 0) {
                try {
                    const results = await apiCall(`/articles/search/query?q=${encodeURIComponent(query)}`);
                    document.getElementById('articles-table-container').innerHTML = renderArticlesTable(results);
                } catch (error) {
                    console.error('Search error:', error);
                }
            } else {
                const articles = await apiCall('/articles?limit=20&offset=0');
                document.getElementById('articles-table-container').innerHTML = renderArticlesTable(articles);
            }
        }, 300);
    });
}

function renderArticlesTable(articles) {
    if (!articles || articles.length === 0) {
        return '<p class="text-muted text-center py-4">No articles found</p>';
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Tags</th>
                    <th>Created</th>
                    <th>Updated</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    articles.forEach((article) => {
        html += `
            <tr>
                <td>
                    <strong>${article.title}</strong>
                    ${article.description ? `<br><small class="text-muted">${article.description}</small>` : ''}
                </td>
                <td>
                    ${article.tags ? article.tags.split(',').map((tag) => `<span class="badge bg-secondary">${tag.trim()}</span>`).join(' ') : '-'}
                </td>
                <td><small>${formatDate(article.created_at)}</small></td>
                <td><small>${formatDate(article.updated_at)}</small></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewArticle('${article.id}')">View</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteArticle('${article.id}')">Delete</button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;
    return html;
}

async function deleteArticle(articleId) {
    if (confirm('Are you sure you want to delete this article?')) {
        try {
            await apiCall(`/articles/${articleId}`, { method: 'DELETE' });
            showAlert('Article deleted successfully', 'success');
            loadKnowledgeBase();
        } catch (error) {
            showAlert('Failed to delete article', 'danger');
        }
    }
}

function viewArticle(articleId) {
    // Placeholder for viewing article details
    showAlert(`Viewing article: ${articleId}`, 'info');
}

// Additional functions for Knowledge Base

async function loadTickets() {
    setActiveNav('nav-tickets');
    document.getElementById('page-title').textContent = 'Ticket Management';
    showLoading(true);

    try {
        const tickets = await apiCall('/tickets?limit=20&offset=0');

        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">
                    <i class="bi bi-cloud-upload"></i> Upload Ticket CSV
                </div>
                <div class="card-body">
                    <form id="upload-tickets-form">
                        <div class="mb-3">
                            <label class="form-label">Select CSV File</label>
                            <div class="file-upload-area" id="ticket-upload-area">
                                <i class="bi bi-cloud-upload"></i>
                                <p>Drag and drop your CSV file here or click to select</p>
                                <small class="text-muted">CSV format: ticket_id,subject,category,created_at,resolved</small>
                                <input type="file" id="ticket-file" accept=".csv" style="display: none;">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-upload"></i> Upload Tickets
                        </button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <i class="bi bi-ticket"></i> Recent Tickets
                </div>
                <div class="card-body">
                    ${renderTicketsTable(tickets)}
                </div>
            </div>
        `;

        setupTicketUpload();

    } catch (error) {
        console.error('Error loading tickets:', error);
        showAlert('Failed to load tickets', 'danger');
    }
}

function setupTicketUpload() {
    const uploadArea = document.getElementById('ticket-upload-area');
    const fileInput = document.getElementById('ticket-file');

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
    });

    document.getElementById('upload-tickets-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select a file', 'warning');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/tickets/upload-csv', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            showAlert(`Imported ${result.imported} tickets, skipped ${result.skipped}`, 'success');
            loadTickets();

        } catch (error) {
            showAlert('Failed to upload tickets', 'danger');
        }
    });
}

function renderTicketsTable(tickets) {
    if (!tickets || tickets.length === 0) {
        return '<p class="text-muted text-center py-4">No tickets</p>';
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Subject</th>
                    <th>Category</th>
                    <th>Created</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    tickets.forEach((ticket) => {
        html += `
            <tr>
                <td><strong>${ticket.ticket_id}</strong></td>
                <td>${ticket.subject}</td>
                <td>${ticket.category || '-'}</td>
                <td><small>${formatDate(ticket.created_at)}</small></td>
                <td><span class="badge ${ticket.resolved ? 'bg-success' : 'bg-warning'}">${ticket.resolved ? 'Resolved' : 'Open'}</span></td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;
    return html;
}
