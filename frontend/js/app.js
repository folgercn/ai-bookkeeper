// 全局状态
let currentBatchId = null;
let currentMode = 'text';

// ----------------- 通用工具 -----------------
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 3000);
}

function updateIcon() {
    if (window.lucide) lucide.createIcons();
}

// ----------------- 认证逻辑 -----------------
let isRegisterMode = false;

async function handleAuth() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    if (!u || !p) return showToast('请输入账号密码');

    try {
        let res;
        if (isRegisterMode) {
            res = await API.register(u, p);
            localStorage.setItem('api_key', res.data.api_key); // 先保存 Key
            showToast('注册成功，正在初始化...');
            await API.initCategories().catch(e => console.error('初始化分类失败:', e));
        } else {
            res = await API.login(u, p);
            localStorage.setItem('api_key', res.data.api_key);
        }
        showApp();
    } catch (err) {
        showToast(err.message);
    }
}

function toggleAuthMode() {
    isRegisterMode = !isRegisterMode;
    const btn = document.getElementById('loginBtn');
    const switchBtn = document.getElementById('showRegisterBtn');
    btn.textContent = isRegisterMode ? '立即注册' : '登录';
    switchBtn.textContent = isRegisterMode ? '返回登录' : '注册账号';
}

function showApp() {
    document.getElementById('authView').style.display = 'none';
    document.getElementById('appView').style.display = 'block';
    loadData();
}

function logout() {
    localStorage.removeItem('api_key');
    location.reload();
}


// 全局状态
let currentPage = 1;
let totalPages = 1;
let filters = {
    startDate: '',
    endDate: '',
    keyword: ''
};
let allExpenses = [];

// ----------------- 核心功能 -----------------
async function loadData(append = false) {
    try {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) loadingIndicator.style.display = 'block';

        const params = {
            page: currentPage,
            pageSize: 20,
            ...filters
        };

        const [expensesRes, summaryRes] = await Promise.all([
            API.getExpenses(params),
            API.getExpensesSummary()
        ]);

        if (append) {
            allExpenses = [...allExpenses, ...expensesRes.data.items];
        } else {
            allExpenses = expensesRes.data.items;
        }

        renderExpenses(allExpenses);

        // 更新分页信息
        totalPages = expensesRes.data.pagination.total_pages;
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = currentPage < totalPages ? 'block' : 'none';
        }

        // 更新统计卡片
        document.getElementById('monthTotal').textContent = `¥ ${summaryRes.data.month_total.toFixed(2)}`;
        document.getElementById('yearTotal').textContent = `¥ ${summaryRes.data.year_total.toFixed(2)}`;

        if (loadingIndicator) loadingIndicator.style.display = 'none';
    } catch (err) {
        console.error(err);
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

function renderExpenses(items) {
    const list = document.getElementById('expenseList');
    if (!items.length) {
        list.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);">暂无记录</div>';
        return;
    }

    list.innerHTML = items.map(i => `
        <div class="glass-card animate-fade-in" style="padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        ${i.remark || i.main_category}
                        ${i.consumer ? `<span style="font-size: 10px; background: rgba(16,185,129,0.1); color: var(--primary); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">${i.consumer}</span>` : ''}
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted);">
                        ${i.date} · ${i.main_category} ${i.sub_category ? `· ${i.sub_category}` : ''}
                        ${i.payee ? `· ${i.payee}` : ''}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-weight: 800; color: var(--text-main);">¥ ${i.amount.toFixed(2)}</div>
                    <div style="display: flex; gap: 4px;">
                        <button onclick="editExpense(${i.id})" class="btn" style="padding: 6px 10px; font-size: 12px;" title="编辑">
                            <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
                        </button>
                        <button onclick="deleteExpense(${i.id})" class="btn" style="padding: 6px 10px; font-size: 12px; color: var(--danger);" title="删除">
                            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    // 重新初始化图标
    updateIcon();
}

// 记账提交
async function handleSubmit() {
    const btn = document.getElementById('submitBtn');

    // 根据当前模式处理不同的输入
    if (currentMode === 'text') {
        const input = document.getElementById('mainInput');
        const content = input.value.trim();

        if (!content) return showToast('请输入记账内容');

        btn.disabled = true;
        btn.innerHTML = '<i class="animate-spin" data-lucide="loader-2"></i> 正在解析...';
        updateIcon();

        try {
            const res = await API.submitRecord('text', content);
            currentBatchId = res.data.batch_id;
            renderStaging(res.data.items);
            input.value = '';
        } catch (err) {
            showToast(err.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="sparkles"></i> 智能记账';
            updateIcon();
        }
    } else if (currentMode === 'image') {
        const imagePreview = document.getElementById('imagePreview');
        const imageData = imagePreview.dataset.imageData;

        if (!imageData) return showToast('请先上传图片');

        btn.disabled = true;
        btn.innerHTML = '<i class="animate-spin" data-lucide="loader-2"></i> 正在识别...';
        updateIcon();

        try {
            const res = await API.submitRecord('image', imageData);
            currentBatchId = res.data.batch_id;
            renderStaging(res.data.items);

            // 清空图片
            imagePreview.style.display = 'none';
            imagePreview.src = '';
            delete imagePreview.dataset.imageData;
        } catch (err) {
            showToast(err.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="sparkles"></i> 智能记账';
            updateIcon();
        }
    } else if (currentMode === 'voice') {
        showToast('语音功能开发中...');
    }
}

// 图片上传处理
function handleImageUpload(file) {
    if (!file || !file.type.startsWith('image/')) {
        showToast('请上传图片文件');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
        imagePreview.dataset.imageData = e.target.result;
    };
    reader.readAsDataURL(file);
}

function renderStaging(items) {
    const area = document.getElementById('stagingArea');
    const list = document.getElementById('stagingList');

    area.style.display = 'block';

    list.innerHTML = items.map(item => `
        <div class="staging-item animate-fade-in">
            <div class="staging-header">
                <span class="staging-amount">¥ ${item.amount.toFixed(2)}</span>
                <span class="staging-meta">#${item.temp_id}</span>
            </div>
            <div class="staging-meta">
                ${item.main_category} / ${item.sub_category || '无'} · ${item.remark || '无备注'}
                ${item.consumer ? `· 👤${item.consumer}` : ''}
            </div>
            ${item.is_duplicate ? '<div style="color: var(--danger); font-size: 11px;">⚠️ 可能重复</div>' : ''}
        </div>
    `).join('');
}

// ----------------- 设置管理 -----------------
async function toggleSettings() {
    const view = document.getElementById('settingsView');
    const isVisible = view.style.display === 'block';
    view.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) {
        await Promise.all([refreshPayees(), refreshAssets()]);
    }
}

async function refreshPayees() {
    const res = await API.getPayees();
    const list = document.getElementById('payeeList');
    list.innerHTML = res.data.map(p => `
        <div class="glass-card" style="padding: 4px 12px; font-size: 12px; display: flex; align-items: center; gap: 8px;">
            ${p.name}
            <i data-lucide="x" style="width: 12px; cursor: pointer;" onclick="deletePayee(${p.id})"></i>
        </div>
    `).join('');
    updateIcon();
}

async function addPayee() {
    const input = document.getElementById('newPayeeName');
    const name = input.value.trim();
    if (!name) return;
    await API.addPayee(name);
    input.value = '';
    refreshPayees();
}

async function deletePayee(id) {
    if (confirm('确认删除该成员？')) {
        await API.deletePayee(id);
        refreshPayees();
    }
}

async function refreshAssets() {
    const res = await API.getAssets();
    const list = document.getElementById('assetList');
    list.innerHTML = res.data.map(a => `
        <div class="glass-card" style="padding: 4px 12px; font-size: 12px; display: flex; align-items: center; gap: 8px;">
            ${a.name}
            <i data-lucide="x" style="width: 12px; cursor: pointer;" onclick="deleteAsset(${a.id})"></i>
        </div>
    `).join('');
    updateIcon();
}

async function addAsset() {
    const input = document.getElementById('newAssetName');
    const name = input.value.trim();
    if (!name) return;
    await API.addAsset(name);
    input.value = '';
    refreshAssets();
}


async function deleteAsset(id) {
    if (confirm('确认删除该资产？')) {
        await API.deleteAsset(id);
        refreshAssets();
    }
}

// 筛选功能
function applyFilters() {
    filters.startDate = document.getElementById('filterStartDate').value;
    filters.endDate = document.getElementById('filterEndDate').value;
    filters.keyword = document.getElementById('filterKeyword').value.trim();

    currentPage = 1;
    allExpenses = [];
    loadData();
}

function resetFilters() {
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    document.getElementById('filterKeyword').value = '';

    filters = { startDate: '', endDate: '', keyword: '' };
    currentPage = 1;
    allExpenses = [];
    loadData();
}

// 加载更多
function loadMore() {
    currentPage++;
    loadData(true);
}

// 编辑功能
let currentEditId = null;

function editExpense(id) {
    const expense = allExpenses.find(e => e.id === id);
    if (!expense) return;

    currentEditId = id;

    // 填充表单
    document.getElementById('editDate').value = expense.date;
    document.getElementById('editAmount').value = expense.amount;
    document.getElementById('editMainCategory').value = expense.main_category || '';
    document.getElementById('editSubCategory').value = expense.sub_category || '';
    document.getElementById('editPayee').value = expense.payee || '';
    document.getElementById('editConsumer').value = expense.consumer || '';
    document.getElementById('editRemark').value = expense.remark || '';

    // 显示对话框
    const modal = document.getElementById('editModal');
    modal.style.display = 'flex';
}

async function saveEdit() {
    if (!currentEditId) return;

    const data = {
        date: document.getElementById('editDate').value,
        amount: parseFloat(document.getElementById('editAmount').value),
        main_category: document.getElementById('editMainCategory').value,
        sub_category: document.getElementById('editSubCategory').value || null,
        payee: document.getElementById('editPayee').value || null,
        consumer: document.getElementById('editConsumer').value || null,
        remark: document.getElementById('editRemark').value || null
    };

    try {
        await API.updateExpense(currentEditId, data);
        closeEditModal();
        showToast('✅ 更新成功');

        // 重新加载当前页面的数据
        currentPage = 1;
        allExpenses = [];
        loadData();
    } catch (err) {
        showToast('更新失败: ' + err.message);
    }
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditId = null;
}

// 删除功能
async function deleteExpense(id) {
    if (!confirm('确认删除这条记录吗？此操作不可恢复！')) return;

    try {
        await API.deleteExpense(id);
        showToast('✅ 删除成功');

        // 重新加载数据
        currentPage = 1;
        allExpenses = [];
        loadData();
    } catch (err) {
        showToast('删除失败: ' + err.message);
    }
}

// 将全局删除函数暴露到 window
window.deletePayee = deletePayee;
window.deleteAsset = deleteAsset;
window.editExpense = editExpense;
window.deleteExpense = deleteExpense;

async function handleInteract() {
    const instr = document.getElementById('interactInput').value.trim();
    if (!instr || !currentBatchId) return;

    try {
        const res = await API.interact(currentBatchId, instr);
        if (res.data.remaining_pending === 0) {
            document.getElementById('stagingArea').style.display = 'none';
            showToast('记账成功并入库');
            loadData();
        } else {
            renderStaging(res.data.items.filter(i => i.status === 'pending').map(i => {
                const data = typeof i.data === 'string' ? JSON.parse(i.data) : i.data;
                return { ...data, temp_id: i.temp_id };
            }));
        }
        document.getElementById('interactInput').value = '';
    } catch (err) {
        showToast(err.message);
    }
}

// 全部确认
async function confirmAll() {
    if (!currentBatchId) return;

    const btn = document.getElementById('confirmAllBtn');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="animate-spin" data-lucide="loader-2"></i> 确认中...';
    updateIcon();

    try {
        const res = await API.interact(currentBatchId, '全部确认');
        document.getElementById('stagingArea').style.display = 'none';
        showToast('✅ 记账成功并入库');
        loadData();
    } catch (err) {
        showToast(err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        updateIcon();
    }
}

// ----------------- 初始化 -----------------
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('api_key')) {
        showApp();
    }

    document.getElementById('loginBtn').onclick = handleAuth;
    document.getElementById('showRegisterBtn').onclick = toggleAuthMode;
    document.getElementById('submitBtn').onclick = handleSubmit;
    document.getElementById('interactBtn').onclick = handleInteract;

    // 全部确认按钮
    const confirmAllBtn = document.getElementById('confirmAllBtn');
    if (confirmAllBtn) confirmAllBtn.onclick = confirmAll;


    // 设置面板绑定
    const settingsBtn = document.getElementById('settingsBtn');
    const exportBtn = document.getElementById('exportBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const addPayeeBtn = document.getElementById('addPayeeBtn');
    const addAssetBtn = document.getElementById('addAssetBtn');

    if (settingsBtn) settingsBtn.onclick = toggleSettings;
    if (exportBtn) exportBtn.onclick = () => API.exportCSV().catch(err => showToast(err.message));
    if (closeSettingsBtn) closeSettingsBtn.onclick = toggleSettings;
    if (addPayeeBtn) addPayeeBtn.onclick = addPayee;
    if (addAssetBtn) addAssetBtn.onclick = addAsset;

    // 筛选和加载更多
    const applyFilterBtn = document.getElementById('applyFilterBtn');
    const resetFilterBtn = document.getElementById('resetFilterBtn');
    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (applyFilterBtn) applyFilterBtn.onclick = applyFilters;
    if (resetFilterBtn) resetFilterBtn.onclick = resetFilters;
    if (loadMoreBtn) loadMoreBtn.onclick = loadMore;

    // 编辑对话框
    const closeEditModalBtn = document.getElementById('closeEditModal');
    const saveEditBtn = document.getElementById('saveEditBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    if (closeEditModalBtn) closeEditModalBtn.onclick = closeEditModal;
    if (saveEditBtn) saveEditBtn.onclick = saveEdit;
    if (cancelEditBtn) cancelEditBtn.onclick = closeEditModal;

    // 点击对话框外部关闭
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.onclick = (e) => {
            if (e.target === editModal) closeEditModal();
        };
    }

    // 模式切换
    document.querySelectorAll('.mode-tab').forEach(tab => {
        tab.onclick = () => {
            document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentMode = tab.dataset.mode;

            // 隐藏所有输入区域
            document.getElementById('textInputArea').style.display = 'none';
            document.getElementById('voiceInputArea').style.display = 'none';
            document.getElementById('imageInputArea').style.display = 'none';

            // 显示当前模式的输入区域
            if (currentMode === 'text') {
                document.getElementById('textInputArea').style.display = 'block';
            } else if (currentMode === 'voice') {
                document.getElementById('voiceInputArea').style.display = 'block';
            } else if (currentMode === 'image') {
                document.getElementById('imageInputArea').style.display = 'block';
            }
        };
    });

    // Enter 键支持
    document.getElementById('mainInput').onkeydown = (e) => {
        if (e.key === 'Enter' && e.ctrlKey) handleSubmit();
    };
    document.getElementById('interactInput').onkeydown = (e) => {
        if (e.key === 'Enter') handleInteract();
    };

    // 图片上传事件绑定
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');

    if (fileInput) {
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) handleImageUpload(file);
        };
    }

    if (dropZone) {
        // 点击上传
        dropZone.onclick = () => {
            if (fileInput) fileInput.click();
        };

        // 拖拽上传
        dropZone.ondragover = (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--primary)';
        };

        dropZone.ondragleave = (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--border)';
        };

        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--border)';
            const file = e.dataTransfer.files[0];
            if (file) handleImageUpload(file);
        };
    }

    // 粘贴图片功能
    document.addEventListener('paste', (e) => {
        // 只在图片模式下处理粘贴
        if (currentMode !== 'image') return;

        const items = e.clipboardData?.items;
        if (!items) return;

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.type.indexOf('image') !== -1) {
                e.preventDefault();
                const file = item.getAsFile();
                if (file) {
                    handleImageUpload(file);
                    showToast('✅ 已粘贴图片');
                }
                break;
            }
        }
    });
});
