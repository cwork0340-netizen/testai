(function () {
  "use strict";

  var STORAGE_KEY = "pointsCard.v1";

  // 兌換獎勵設定（章數由小到大）
  var REWARDS = [
    { id: "r1",  cost: 1,  title: "50元玩具",        sub: "最多 50 元" },
    { id: "r2",  cost: 2,  title: "100 元以內玩具或文具", sub: "最多 100 元" },
    { id: "r5",  cost: 5,  title: "300 元以內玩具",   sub: "最多 300 元" },
    { id: "r10", cost: 10, title: "新書包",           sub: "最多 700 元" },
    { id: "r30", cost: 30, title: "新書包",           sub: "最多 2500 元" }
  ];

  var defaultState = { name: "April", stamps: 0, history: [] };

  function loadState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return Object.assign({}, defaultState);
      var parsed = JSON.parse(raw);
      return {
        name: typeof parsed.name === "string" ? parsed.name : defaultState.name,
        stamps: typeof parsed.stamps === "number" ? parsed.stamps : 0,
        history: Array.isArray(parsed.history) ? parsed.history : []
      };
    } catch (e) {
      return Object.assign({}, defaultState);
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      /* localStorage 不可用時忽略 */
    }
  }

  var state = loadState();

  // --- DOM 取得 ---
  var $ = function (sel) { return document.querySelector(sel); };

  var els = {
    count: $("#count"),
    countStamp: $("#countStamp"),
    owner: $("#stampOwner"),
    ownerStamp: $("#stampOwnerStamp"),
    childName: $("#childName"),
    rewardList: $("#rewardList"),
    stampGrid: $("#stampGrid"),
    historyList: $("#historyList"),
    historyEmpty: $("#historyEmpty"),
    nameInput: $("#nameInput"),
    toast: $("#toast")
  };

  // --- 顯示更新 ---
  function fmtTime(ts) {
    var d = new Date(ts);
    function p(n) { return n < 10 ? "0" + n : "" + n; }
    return d.getFullYear() + "/" + p(d.getMonth() + 1) + "/" + p(d.getDate()) +
      " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }

  function renderCounts() {
    els.count.textContent = state.stamps;
    els.countStamp.textContent = state.stamps;
    els.owner.textContent = state.name;
    els.ownerStamp.textContent = state.name;
    els.childName.textContent = state.name;
    els.nameInput.value = state.name;
  }

  function renderRewards() {
    var frag = document.createDocumentFragment();
    REWARDS.forEach(function (r) {
      var enough = state.stamps >= r.cost;

      var card = document.createElement("div");
      card.className = "reward" + (enough ? "" : " is-locked");

      var info = document.createElement("div");
      info.className = "reward-info";
      info.innerHTML =
        '<div class="reward-cost">' + r.cost + ' 章</div>' +
        '<div class="reward-title"></div>' +
        '<div class="reward-sub"></div>';
      info.querySelector(".reward-title").textContent = r.title;
      info.querySelector(".reward-sub").textContent = r.sub;

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "redeem-btn";
      btn.textContent = "兌換";
      btn.disabled = !enough;
      btn.addEventListener("click", function () { redeem(r); });

      card.appendChild(info);
      card.appendChild(btn);
      frag.appendChild(card);
    });
    els.rewardList.innerHTML = "";
    els.rewardList.appendChild(frag);
  }

  function renderStampGrid() {
    var total = Math.max(10, Math.ceil(state.stamps / 5) * 5);
    var frag = document.createDocumentFragment();
    for (var i = 0; i < total; i++) {
      var dot = document.createElement("div");
      dot.className = "stamp-dot" + (i < state.stamps ? " filled" : "");
      if (i < state.stamps) dot.textContent = "★";
      frag.appendChild(dot);
    }
    els.stampGrid.innerHTML = "";
    els.stampGrid.appendChild(frag);
  }

  function renderHistory() {
    els.historyList.innerHTML = "";
    if (!state.history.length) {
      els.historyEmpty.hidden = false;
      return;
    }
    els.historyEmpty.hidden = true;
    var frag = document.createDocumentFragment();
    state.history.forEach(function (h) {
      var li = document.createElement("li");
      li.className = "history-item " + (h.type === "redeem" ? "is-redeem" : "is-stamp");

      var main = document.createElement("div");
      main.className = "h-main";
      var title = document.createElement("div");
      title.className = "h-title";
      title.textContent = h.title;
      var sub = document.createElement("div");
      sub.className = "h-sub";
      sub.textContent = h.sub || "";
      main.appendChild(title);
      if (h.sub) main.appendChild(sub);

      var time = document.createElement("div");
      time.className = "h-time";
      time.textContent = fmtTime(h.ts);

      li.appendChild(main);
      li.appendChild(time);
      frag.appendChild(li);
    });
    els.historyList.appendChild(frag);
  }

  function renderAll() {
    renderCounts();
    renderRewards();
    renderStampGrid();
    renderHistory();
  }

  // --- 行為 ---
  function addHistory(entry) {
    entry.ts = Date.now();
    state.history.unshift(entry);
    if (state.history.length > 200) state.history.length = 200;
  }

  function redeem(reward) {
    if (state.stamps < reward.cost) {
      showToast("印章不足，無法兌換");
      return;
    }
    state.stamps -= reward.cost;
    // 修正：兌換後記錄兌換了什麼
    addHistory({
      type: "redeem",
      title: "兌換 " + reward.title,
      sub: "扣除 " + reward.cost + " 章 · " + reward.sub
    });
    saveState();
    renderAll();
    showToast("已兌換：" + reward.title);
  }

  function addStamp() {
    state.stamps += 1;
    addHistory({ type: "stamp", title: "蓋章 +1", sub: "目前 " + state.stamps + " 章" });
    saveState();
    renderAll();
  }

  function removeStamp() {
    if (state.stamps <= 0) return;
    state.stamps -= 1;
    addHistory({ type: "stamp", title: "取消蓋章 -1", sub: "目前 " + state.stamps + " 章" });
    saveState();
    renderAll();
  }

  var toastTimer = null;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    // 強制 reflow 讓 transition 生效
    void els.toast.offsetWidth;
    els.toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      els.toast.classList.remove("show");
      setTimeout(function () { els.toast.hidden = true; }, 220);
    }, 1800);
  }

  // --- 分頁切換 ---
  function switchTab(name) {
    document.querySelectorAll(".tab").forEach(function (t) {
      t.classList.toggle("is-active", t.dataset.tab === name);
    });
    document.querySelectorAll(".panel").forEach(function (p) {
      p.hidden = p.dataset.panel !== name;
    });
  }

  // --- 事件綁定 ---
  document.querySelectorAll(".tab").forEach(function (t) {
    t.addEventListener("click", function () { switchTab(t.dataset.tab); });
  });

  // 左上叉叉：可點，嘗試關閉視窗，無法關閉時提示
  $("#closeBtn").addEventListener("click", function () {
    try {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({ type: "close-points-card" }, "*");
      }
    } catch (e) { /* ignore */ }
    var closed = false;
    try { window.close(); closed = !!window.closed; } catch (e) {}
    if (!closed) showToast("已關閉（回到上一頁）");
    if (history.length > 1) history.back();
  });

  $("#addStampBtn").addEventListener("click", addStamp);
  $("#removeStampBtn").addEventListener("click", removeStamp);

  $("#clearHistoryBtn").addEventListener("click", function () {
    if (!state.history.length) return;
    if (window.confirm("確定要清除所有紀錄嗎？")) {
      state.history = [];
      saveState();
      renderHistory();
      showToast("已清除紀錄");
    }
  });

  $("#saveNameBtn").addEventListener("click", function () {
    var v = els.nameInput.value.trim();
    if (!v) { showToast("請輸入名稱"); return; }
    state.name = v;
    saveState();
    renderCounts();
    showToast("已儲存");
  });

  renderAll();
})();
