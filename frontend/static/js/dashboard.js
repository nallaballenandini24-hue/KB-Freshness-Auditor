// Dashboard page functionality

async function loadDashboard() {
    setActiveNav('nav-dashboard');
    document.getElementById('page-title').textContent = 'Dashboard';
    showLoading(true);

    try {
        const stats = await apiCall('/audits/dashboard/stats');
        const recentAudits = await apiCall('/audits/recent');
        const topStale = await apiCall('/audits/stale/top');

        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div class="row gap-4 mb-4">
                <div class="col-lg-3 col-md-6">
                    <div class="card stat-card">
                        <div class="card-body">
                            <div class="stat-value">${formatNumber(stats.total_articles)}</div>
                            <div class="stat-label">Total Articles</div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card stat-card stat-card-fresh">
                        <div class="card-body">
                            <div class="stat-value">${formatNumber(stats.fresh_articles)}</div>
                            <div class="stat-label">Fresh Articles</div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card stat-card stat-card-warning">
                        <div class="card-body">
                            <div class="stat-value">${formatNumber(stats.warning_articles)}</div>
                            <div class="stat-label">Warning Articles</div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card stat-card stat-card-stale">
                        <div class="card-body">
                            <div class="stat-value">${formatNumber(stats.stale_articles)}</div>
                            <div class="stat-label">Stale Articles</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row gap-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-bar-chart"></i> Freshness Distribution
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="freshness-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-list"></i> Recent Audits
                        </div>
                        <div class="card-body">
                            ${renderRecentAudits(recentAudits)}
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mt-4">
                <div class="card-header">
                    <i class="bi bi-exclamation-triangle"></i> Top 10 Stale Articles
                </div>
                <div class="card-body">
                    ${renderTopStaleTable(topStale)}
                </div>
            </div>
        `;

        // Render freshness distribution chart
        renderFreshnessChart(stats);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('Failed to load dashboard data', 'danger');
    }
}

function renderFreshnessChart(stats) {
    const ctx = document.getElementById('freshness-chart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Fresh', 'Warning', 'Stale'],
                datasets: [
                    {
                        data: [stats.fresh_articles, stats.warning_articles, stats.stale_articles],
                        backgroundColor: ['#198754', '#ffc107', '#dc3545'],
                        borderColor: '#fff',
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
            },
        });
    }
}

function renderRecentAudits(audits) {
    if (!audits || audits.length === 0) {
        return '<p class="text-muted">No recent audits</p>';
    }

    let html = '<ul class="list-group list-group-flush">';
    audits.forEach((audit) => {
        html += `
            <li class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${audit.article_id}</strong>
                        <br>
                        <small class="text-muted">${formatDate(audit.audit_date)}</small>
                    </div>
                    <span class="badge badge-${audit.status}">${audit.status.toUpperCase()}</span>
                </div>
            </li>
        `;
    });
    html += '</ul>';
    return html;
}

function renderTopStaleTable(articles) {
    if (!articles || articles.length === 0) {
        return '<p class="text-muted text-center py-4">No stale articles</p>';
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Article ID</th>
                    <th>Freshness Score</th>
                    <th>Age (Days)</th>
                    <th>Ticket Count</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    articles.forEach((article) => {
        html += `
            <tr>
                <td>${article.article_id}</td>
                <td>${article.freshness_score.toFixed(2)}</td>
                <td>${article.article_age_days}</td>
                <td>${article.ticket_count}</td>
                <td><span class="badge badge-${article.status}">${article.status}</span></td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;
    return html;
}
