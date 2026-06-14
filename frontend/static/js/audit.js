// Audit page functionality

async function loadAudit() {
    setActiveNav('nav-audit');
    document.getElementById('page-title').textContent = 'Freshness Audit';
    showLoading(true);

    try {
        const latestJob = await apiCall('/audits/status/latest').catch(() => null);

        const contentArea = document.getElementById('content-area');
        let jobStatusHtml = '';

        if (latestJob) {
            const progress = latestJob.total_articles > 0 
                ? Math.round((latestJob.processed_articles / latestJob.total_articles) * 100) 
                : 0;

            jobStatusHtml = `
                <div class="card mb-4">
                    <div class="card-header">
                        <i class="bi bi-hourglass"></i> Audit Progress
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <small class="text-muted">Status:</small>
                                <p class="mb-0">
                                    <span class="badge bg-${latestJob.status === 'completed' ? 'success' : latestJob.status === 'failed' ? 'danger' : 'info'}">
                                        ${latestJob.status.toUpperCase()}
                                    </span>
                                </p>
                            </div>
                            <div class="col-md-6">
                                <small class="text-muted">Progress:</small>
                                <p class="mb-0">${latestJob.processed_articles} / ${latestJob.total_articles}</p>
                            </div>
                        </div>
                        <div class="progress">
                            <div class="progress-bar" style="width: ${progress}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }

        contentArea.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">
                    <i class="bi bi-play-circle"></i> Run Audit
                </div>
                <div class="card-body">
                    <p class="text-muted">Scan all KB articles and calculate freshness scores based on age, ticket references, and update frequency.</p>
                    <button class="btn btn-primary btn-lg" id="run-audit-btn">
                        <i class="bi bi-play-fill"></i> Start Audit
                    </button>
                </div>
            </div>

            ${jobStatusHtml}

            <div class="card">
                <div class="card-header">
                    <i class="bi bi-table"></i> Recent Audits
                </div>
                <div class="card-body">
                    <div id="recent-audits-container">
                        <p class="text-muted">Loading...</p>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('run-audit-btn').addEventListener('click', runAudit);
        loadRecentAudits();

    } catch (error) {
        console.error('Error loading audit page:', error);
        showAlert('Failed to load audit page', 'danger');
    }
}

async function runAudit() {
    const btn = document.getElementById('run-audit-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Running...';

    try {
        const job = await apiCall('/audits/run', { method: 'POST' });
        showAlert('Audit started successfully. Job ID: ' + job.id, 'success');

        // Poll for status
        pollAuditStatus(job.id);

    } catch (error) {
        showAlert('Failed to start audit', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-fill"></i> Start Audit';
    }
}

async function pollAuditStatus(jobId) {
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes with 5-second intervals

    const pollInterval = setInterval(async () => {
        attempts++;

        try {
            const job = await apiCall(`/audits/status/${jobId}`);

            const progress = job.total_articles > 0 
                ? Math.round((job.processed_articles / job.total_articles) * 100) 
                : 0;

            // Update progress UI
            const statusBadge = document.querySelector('.badge');
            if (statusBadge) {
                statusBadge.textContent = job.status.toUpperCase();
                statusBadge.className = `badge bg-${job.status === 'completed' ? 'success' : job.status === 'failed' ? 'danger' : 'info'}`;
            }

            if (job.status === 'completed' || job.status === 'failed' || attempts >= maxAttempts) {
                clearInterval(pollInterval);

                if (job.status === 'completed') {
                    showAlert('Audit completed successfully', 'success');
                    loadAudit();
                } else if (job.status === 'failed') {
                    showAlert('Audit failed: ' + (job.error_message || 'Unknown error'), 'danger');
                }
            }

        } catch (error) {
            console.error('Error polling audit status:', error);
        }
    }, 5000);
}

async function loadRecentAudits() {
    try {
        const audits = await apiCall('/audits/recent?limit=20');
        const container = document.getElementById('recent-audits-container');

        if (!audits || audits.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No audits yet</p>';
            return;
        }

        let html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Article ID</th>
                        <th>Freshness Score</th>
                        <th>Status</th>
                        <th>Age (Days)</th>
                        <th>Tickets</th>
                        <th>Audit Date</th>
                    </tr>
                </thead>
                <tbody>
        `;

        audits.forEach((audit) => {
            html += `
                <tr>
                    <td>${audit.article_id}</td>
                    <td><strong>${audit.freshness_score.toFixed(2)}</strong></td>
                    <td><span class="badge badge-${audit.status}">${audit.status}</span></td>
                    <td>${audit.article_age_days}</td>
                    <td>${audit.ticket_count}</td>
                    <td><small>${formatDate(audit.audit_date)}</small></td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading recent audits:', error);
    }
}

async function loadRecommendations() {
    setActiveNav('nav-recommendations');
    document.getElementById('page-title').textContent = 'AI Recommendations Center';
    showLoading(true);

    try {
        const pending = await apiCall('/recommendations/pending?limit=20');

        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <i class="bi bi-lightbulb"></i> Pending Recommendations
                </div>
                <div class="card-body">
                    <div id="recommendations-container">
                        ${renderRecommendationsTable(pending)}
                    </div>
                </div>
            </div>
        `;

    } catch (error) {
        console.error('Error loading recommendations:', error);
        showAlert('Failed to load recommendations', 'danger');
    }
}

function renderRecommendationsTable(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return '<p class="text-muted text-center py-4">No pending recommendations</p>';
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Article ID</th>
                    <th>Type</th>
                    <th>Confidence</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    recommendations.forEach((rec) => {
        html += `
            <tr>
                <td>${rec.article_id}</td>
                <td>${rec.recommendation_type}</td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" style="width: ${rec.confidence_score * 100}%">
                            ${(rec.confidence_score * 100).toFixed(0)}%
                        </div>
                    </div>
                </td>
                <td><small>${formatDate(rec.created_at)}</small></td>
                <td>
                    <button class="btn btn-sm btn-outline-success" onclick="acceptRecommendation('${rec.id}')">
                        <i class="bi bi-check"></i> Accept
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="rejectRecommendation('${rec.id}')">
                        <i class="bi bi-x"></i> Reject
                    </button>
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

async function acceptRecommendation(recId) {
    try {
        await apiCall(`/recommendations/${recId}/accept`, { method: 'POST' });
        showAlert('Recommendation accepted', 'success');
        loadRecommendations();
    } catch (error) {
        showAlert('Failed to accept recommendation', 'danger');
    }
}

async function rejectRecommendation(recId) {
    try {
        await apiCall(`/recommendations/${recId}/reject`, { method: 'POST' });
        showAlert('Recommendation rejected', 'success');
        loadRecommendations();
    } catch (error) {
        showAlert('Failed to reject recommendation', 'danger');
    }
}
