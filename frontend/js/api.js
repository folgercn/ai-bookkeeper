// 使用相对路径,支持反向代理部署
// 开发环境: 直接访问后端 http://127.0.0.1:8000/v1
// 生产环境: 通过反向代理 /api 访问后端
const BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000/v1'
    : '/api/v1';

class API {
    static getHeaders() {
        const apiKey = localStorage.getItem('api_key');
        return {
            'Content-Type': 'application/json',
            'Authorization': apiKey ? `Bearer ${apiKey}` : ''
        };
    }

    static async request(endpoint, method = 'GET', body = null) {
        const headers = this.getHeaders();
        console.log(`[API Request] ${method} ${endpoint}`, headers);
        const options = {
            method,
            headers: headers
        };
        if (body) options.body = JSON.stringify(body);

        try {
            const resp = await fetch(`${BASE_URL}${endpoint}`, options);
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error?.message || '请求失败');
            return data;
        } catch (err) {
            console.error(`API Error (${endpoint}):`, err);
            throw err;
        }
    }

    static async login(username, password) {
        return this.request('/auth/login', 'POST', { username, password });
    }

    static async register(username, password) {
        return this.request('/auth/register', 'POST', { username, password });
    }

    static async submitRecord(type, content) {
        return this.request('/record', 'POST', { type, content });
    }

    static async interact(batchId, instruction) {
        return this.request('/record/interact', 'POST', { batch_id: batchId, instruction });
    }

    static async getExpenses(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.pageSize) queryParams.append('page_size', params.pageSize);
        if (params.startDate) queryParams.append('start_date', params.startDate);
        if (params.endDate) queryParams.append('end_date', params.endDate);
        if (params.mainCategory) queryParams.append('main_category', params.mainCategory);
        if (params.keyword) queryParams.append('keyword', params.keyword);

        const query = queryParams.toString();
        return this.request(`/expenses${query ? '?' + query : ''}`);
    }

    static async updateExpense(id, data) {
        return this.request(`/expenses/${id}`, 'PUT', data);
    }

    static async deleteExpense(id) {
        return this.request(`/expenses/${id}`, 'DELETE');
    }

    static async getExpensesSummary() {
        return this.request('/expenses/summary');
    }

    static async getPayees() { return this.request('/config/payees'); }
    static async addPayee(name) { return this.request('/config/payees', 'POST', { name }); }
    static async deletePayee(id) { return this.request(`/config/payees/${id}`, 'DELETE'); }

    static async getAssets() { return this.request('/config/assets'); }
    static async addAsset(name) { return this.request('/config/assets', 'POST', { name }); }
    static async deleteAsset(id) { return this.request(`/config/assets/${id}`, 'DELETE'); }

    static async initCategories() {
        return this.request('/config/categories/init', 'POST');
    }

    static async exportCSV() {
        const apiKey = localStorage.getItem('api_key');
        const url = `${BASE_URL}/export/csv`;
        const resp = await fetch(url, {
            headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        if (!resp.ok) throw new Error('导出失败');

        const blob = await resp.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `账单导出_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        a.remove();
    }
}
