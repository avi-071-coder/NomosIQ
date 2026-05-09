class NomosIQ {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        this.bindEvents();
        
        // Handle initial page from URL if needed, else dashboard
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('page') || 'dashboard';
        const q = urlParams.get('q');
        this.loadPage(page, false, q);
    }



    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-btn, .feature-card').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                if (page) {
                    this.loadPage(page);
                }
            });
        });



        // Browser Back/Forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.loadPage(e.state.page, false, e.state.q);
            } else {
                this.loadPage('dashboard', false);
            }
        });
    }

    // Custom back function for UI buttons
    goBack() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            this.loadPage('dashboard');
        }
    }

    async loadPage(page, pushState = true, q = null) {
        this.currentPage = page;

        // Update History
        if (pushState) {
            let url = page === 'dashboard' ? window.location.pathname : `?page=${page}`;
            if (q) url += `&q=${encodeURIComponent(q)}`;
            window.history.pushState({ page, q }, '', url);
        }

        // Update nav
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-page="${page}"]`)?.classList.add('active');

        // Hide all pages
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

        if (page === 'dashboard') {
            document.getElementById('dashboard').classList.add('active');
            window.scrollTo(0, 0);
            return;
        }

        // Remove existing page if any to avoid ID conflicts
        const existingPage = document.getElementById(page);
        if (existingPage) existingPage.remove();

        // Load page content with cache buster
        const timestamp = new Date().getTime();
        const response = await fetch(`components/${page}.html?v=${timestamp}`);
        const html = await response.text();
        const container = document.createElement('section');
        container.id = page;
        container.className = 'page active';
        container.innerHTML = html;
        document.querySelector('.main').appendChild(container);
        
        window.scrollTo(0, 0);

        // Initialize page
        this.initPage(page, container, q);
    }

    initPage(page, container, q = null) {
        if (page === 'analyzer') {
            this.initAnalyzer(container);
        } else if (page === 'chat') {
            this.initChat(container);
        } else if (page === 'explorer') {
            this.initExplorer(container, q);
        }
    }

    initAnalyzer(container) {
        // Tab switching logic
        const tabBtns = container.querySelectorAll('.a-tab');
        const tabPanes = container.querySelectorAll('.tab-pane');
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                container.querySelector(`.tab-pane[data-tab="${btn.dataset.tab}"]`).classList.add('active');
            });
        });

        container.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const resultsDiv = container.querySelector('.results');
            
            resultsDiv.innerHTML = '<div class="loading">Analyzing document...</div>';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    this.renderAnalysis(data.data);
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="error">Analysis failed. Please try again.</div>';
            }
        });
    }

    initChat(container) {
        const messagesDiv = container.querySelector('.chat-messages');
        const input = container.querySelector('.chat-input input');

        const sendMessage = async () => {
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            messagesDiv.innerHTML += `
                <div class="message user">${message}</div>
            `;
            input.value = '';
            
            // Show typing
            messagesDiv.innerHTML += '<div class="message bot typing">LegalChat is typing...</div>';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `message=${encodeURIComponent(message)}`
                });
                const data = await response.json();
                
                const typing = messagesDiv.querySelector('.typing');
                if (typing) typing.remove();
                
                if (data.success) {
                    this.renderChatResponse(messagesDiv, data.data);
                } else {
                    messagesDiv.innerHTML += `<div class="message bot error">Sorry, the server returned an error: ${data.detail || 'Unknown error'}</div>`;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            } catch (error) {
                const typing = messagesDiv.querySelector('.typing');
                if (typing) typing.remove();
                messagesDiv.innerHTML += '<div class="message bot error">Sorry, I encountered a network error. Please try again.</div>';
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        };

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        container.querySelector('.send-btn').addEventListener('click', sendMessage);

        // Handle suggested questions
        const suggestionBtns = container.querySelectorAll('.suggestion-btn');
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                input.value = btn.innerText;
                sendMessage();
            });
        });
    }

    initExplorer(container, initialQuery = null) {
        const searchInput = container.querySelector('.search-input');
        const resultsDiv = container.querySelector('.explorer-results');
        const staticContent = container.querySelector('.static-explorer-content');

        const search = async (q = null) => {
            const query = q !== null ? q : (searchInput.value || "");
            
            if (q !== null) searchInput.value = q;

            if (!query) {
                if (staticContent) staticContent.style.display = 'block';
                resultsDiv.style.display = 'none';
                resultsDiv.innerHTML = '';
                return;
            }
            
            if (staticContent) staticContent.style.display = 'none';
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">Searching laws...</div>';

            try {
                const response = await fetch(`/api/explore?query=${encodeURIComponent(query)}&category=`);
                const data = await response.json();
                
                if (data.success) {
                    this.renderExplorerResults(resultsDiv, data.data);
                } else {
                    resultsDiv.innerHTML = `<div class="error">Search failed: ${data.detail || 'Unknown error'}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="error">Search failed. Please check your connection.</div>';
            }
        };

        searchInput.addEventListener('input', () => {
            clearTimeout(window.searchTimeout);
            window.searchTimeout = setTimeout(() => search(), 300);
        });

        if (initialQuery) {
            search(initialQuery);
        }
    }
    
    searchExplorer(query) {
        this.loadPage('explorer', true, query);
    }

    renderAnalysis(data) {
        const container = document.getElementById('analyzer-results');
        if (!container) return;
        let tableRows = '';
        data.sections.forEach((section, index) => {
            let riskClass = "tag-clear";
            let riskText = "Clear";
            
            if (section.impact && section.impact.toLowerCase().includes('high')) {
                riskClass = "tag-risk"; riskText = "Risk Flag";
            } else if (section.impact && section.impact.toLowerCase().includes('ambiguous')) {
                riskClass = "tag-ambiguous"; riskText = "Ambiguous";
            } else if (section.impact && section.impact.toLowerCase().includes('medium')) {
                riskClass = "tag-ambiguous"; riskText = "Review";
            }
            
            tableRows += `
                <tr>
                    <td style="width: 70%">${section.title}</td>
                    <td style="width: 30%; text-align: right;"><span class="${riskClass}">${riskText}</span></td>
                </tr>
            `;
        });

        container.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <h3 style="font-size: 1.2rem; color: var(--text-primary); margin-bottom: 1rem;">Clause Review</h3>
                <table class="clause-table">
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
            
            <div>
                <h3 style="font-size: 1.2rem; color: var(--text-primary); margin-bottom: 1rem;">Key Summary</h3>
                <p style="color: var(--text-secondary); line-height: 1.8;">${data.summary}</p>
            </div>
        `;
    }

    renderChatResponse(container, data) {
        // Parse markdown if marked is available, otherwise use a fallback
        let parsedAnswer = data.answer;
        if (typeof marked !== 'undefined') {
            parsedAnswer = marked.parse(data.answer);
        } else {
            parsedAnswer = parsedAnswer.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        }

        const messageHtml = `
            <div class="message bot">
                <div class="markdown-content" style="line-height: 1.8;">${parsedAnswer}</div>
                ${data.risk_level ? `
                    <div class="risk-indicator risk-${data.risk_level.toLowerCase()} mt-2">
                        Risk: ${data.risk_level}
                    </div>
                ` : ''}
                ${data.sections?.length ? `
                    <div class="mt-2">
                        <strong>Relevant Laws:</strong> ${data.sections.join(', ')}
                    </div>
                ` : ''}
                ${data.next_steps?.length ? `
                    <div class="mt-2">
                        <strong>Next Steps:</strong>
                        <ul>${data.next_steps.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                ` : ''}
                <div class="mt-2 text-sm opacity-75">*Not legal advice. Consult a lawyer.</div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', messageHtml);
        container.scrollTop = container.scrollHeight;
    }

    renderExplorerResults(container, results) {
        if (!results.length) {
            return container.innerHTML = '<div class="empty-state">No laws found. Try different keywords.</div>';
        }

        container.innerHTML = results.map(result => `
            <div class="explorer-result">
                <h4>${result.title} <span class="category-badge">${result.category.toUpperCase()}</span></h4>
                <p>${result.explanation}</p>
                <div class="result-meta">
                    <span>Applies: ${result.applies}</span>
                    <button class="btn btn-secondary btn-sm" onclick="app.askLegalChat('${result.title}')">
                        Ask LegalChat
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// Initialize app
const app = new NomosIQ();
window.app = app;