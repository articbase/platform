from __future__ import annotations


def render_order_management_page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Order Manager</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Arial, sans-serif;
    }
    body {
      margin: 0;
      background: #f8fafc;
      color: #1f2937;
      font-size: 13px;
    }
    main {
      max-width: 1100px;
      margin: 0 auto;
      padding: 16px;
    }
    h1, h2 {
      margin: 0 0 10px;
    }
    h1 {
      font-size: 22px;
    }
    h2 {
      font-size: 15px;
    }
    .layout {
      display: grid;
      gap: 12px;
      grid-template-columns: minmax(0, 1.7fr) minmax(320px, 1fr);
      align-items: start;
    }
    .card {
      background: #ffffff;
      border: 1px solid #d7dee8;
      border-radius: 8px;
      padding: 12px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 7px 8px;
      border-bottom: 1px solid #e5e7eb;
      vertical-align: top;
      text-align: left;
      font-size: 12px;
    }
    th {
      color: #475569;
      font-weight: 600;
    }
    .muted {
      color: #64748b;
      margin: 0 0 12px;
      font-size: 12px;
    }
    .status {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      background: #e2e8f0;
      color: #334155;
      font-size: 11px;
      font-weight: 700;
    }
    .actions {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 6px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }
    .primary {
      background: #2563eb;
      color: #ffffff;
    }
    .secondary {
      background: #e2e8f0;
      color: #0f172a;
    }
    .danger {
      background: #dc2626;
      color: #ffffff;
    }
    input, select {
      width: 100%;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 7px 8px;
      font: inherit;
      box-sizing: border-box;
    }
    label {
      display: block;
      margin-bottom: 10px;
      font-size: 12px;
      font-weight: 600;
    }
    .form-grid {
      display: grid;
      grid-template-columns: 88px 1fr 88px 1fr;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
    }
    .form-grid label {
      margin: 0;
    }
    .hint {
      margin-top: 4px;
      font-size: 11px;
      color: #64748b;
      font-weight: 400;
    }
    .banner {
      display: none;
      margin-bottom: 12px;
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }
    .banner.success {
      display: block;
      background: #dcfce7;
      color: #166534;
    }
    .banner.error {
      display: block;
      background: #fee2e2;
      color: #991b1b;
    }
    .empty {
      padding: 14px;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      color: #64748b;
      text-align: center;
    }
    .stack {
      display: grid;
      gap: 12px;
    }
    .table-wrap {
      overflow-x: auto;
    }
    code {
      font-size: 11px;
    }
    .section-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 8px;
    }
    .section-head .muted {
      margin: 0;
    }
    .toolbar {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
    }
    .line-items {
      display: grid;
      gap: 6px;
      margin-bottom: 10px;
    }
    .line-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 88px 72px;
      gap: 6px;
      align-items: center;
    }
    .line-row input {
      margin: 0;
    }
    .line-row button {
      padding: 7px 8px;
    }
    .mini-form {
      display: grid;
      gap: 8px;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #e5e7eb;
    }
    .mini-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    @media (max-width: 960px) {
      .layout {
        grid-template-columns: 1fr;
      }
      .form-grid {
        grid-template-columns: 1fr;
      }
      .line-row {
        grid-template-columns: 1fr;
      }
      .mini-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1>Order Manager</h1>
    <p class="muted">View, edit, update, and delete existing orders while keeping inventory stock consistent.</p>
    <div id="banner" class="banner"></div>
    <div class="layout">
      <section class="card">
        <div class="section-head">
          <h2>Orders</h2>
          <div class="toolbar">
            <span class="muted">Create, edit, or delete.</span>
            <button class="secondary" type="button" id="new-order">New Order</button>
          </div>
        </div>
        <div id="orders-container" class="empty">Loading orders...</div>
      </section>
      <div class="stack">
        <section class="card">
          <div class="section-head">
            <h2 id="form-title">New Order</h2>
            <span class="muted">Simple line entry</span>
          </div>
          <form id="order-form">
            <div class="form-grid">
              <label for="order-id">Order ID</label>
              <input id="order-id" type="text" disabled>
              <label for="status">Status</label>
              <input id="status" name="status" type="text" required maxlength="32">
            </div>
            <label for="customer-id">
              Customer ID
              <input id="customer-id" name="customer_id" type="text" required maxlength="128">
            </label>
            <label>
              Order Lines
              <div id="line-items" class="line-items"></div>
              <div class="actions">
                <button class="secondary" type="button" id="add-line">Add Line</button>
              </div>
              <div class="hint">Pick an inventory item from the list, then enter the quantity.</div>
            </label>
            <div class="actions">
              <button class="primary" type="submit" id="submit-order">Add Order</button>
              <button class="secondary" type="button" id="cancel-edit">Clear</button>
            </div>
          </form>
        </section>
        <section class="card">
          <div class="section-head">
            <h2>Inventory</h2>
            <span class="muted">Current stock and add item</span>
          </div>
          <div id="inventory-container" class="empty">Loading inventory...</div>
          <form id="inventory-form" class="mini-form">
            <div class="mini-grid">
              <label for="inventory-sku">
                SKU
                <input id="inventory-sku" type="text" required maxlength="64" placeholder="MACBOOK-16">
              </label>
              <label for="inventory-name">
                Name
                <input id="inventory-name" type="text" required maxlength="255" placeholder="MacBook Pro 16">
              </label>
            </div>
            <div class="mini-grid">
              <label for="inventory-stock">
                Stock
                <input id="inventory-stock" type="number" min="0" step="1" required value="1">
              </label>
              <label for="inventory-price">
                Unit Price (cents)
                <input id="inventory-price" type="number" min="1" step="1" required placeholder="249999">
              </label>
            </div>
            <div class="actions">
              <button class="primary" type="submit">Add Inventory</button>
            </div>
          </form>
        </section>
      </div>
    </div>
  </main>
  <script>
    const state = {
      orders: [],
      inventory: [],
      editingOrderId: null,
    };

    const banner = document.getElementById("banner");
    const ordersContainer = document.getElementById("orders-container");
    const inventoryContainer = document.getElementById("inventory-container");
    const inventoryForm = document.getElementById("inventory-form");
    const inventorySkuInput = document.getElementById("inventory-sku");
    const inventoryNameInput = document.getElementById("inventory-name");
    const inventoryStockInput = document.getElementById("inventory-stock");
    const inventoryPriceInput = document.getElementById("inventory-price");
    const orderForm = document.getElementById("order-form");
    const orderIdInput = document.getElementById("order-id");
    const customerIdInput = document.getElementById("customer-id");
    const statusInput = document.getElementById("status");
    const lineItemsContainer = document.getElementById("line-items");
    const cancelEditButton = document.getElementById("cancel-edit");
    const newOrderButton = document.getElementById("new-order");
    const addLineButton = document.getElementById("add-line");
    const formTitle = document.getElementById("form-title");
    const submitOrderButton = document.getElementById("submit-order");

    function showBanner(kind, message) {
      banner.className = "banner " + kind;
      banner.textContent = message;
    }

    function clearBanner() {
      banner.className = "banner";
      banner.textContent = "";
    }

    function formatMoney(cents) {
      return "$" + (cents / 100).toFixed(2);
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function inventoryOptionsHtml(selectedSku) {
      const options = ['<option value="">Select item</option>'];
      for (const item of state.inventory) {
        const selected = item.sku === selectedSku ? ' selected' : '';
        options.push(
          '<option value="' + escapeHtml(item.sku) + '"' + selected + '>' +
            escapeHtml(item.name) + ' (' + escapeHtml(item.sku) + ', stock ' + item.stock + ')' +
          '</option>'
        );
      }

      if (selectedSku && !state.inventory.some((item) => item.sku === selectedSku)) {
        options.push('<option value="' + escapeHtml(selectedSku) + '" selected>' + escapeHtml(selectedSku) + "</option>");
      }

      return options.join("");
    }

    function renderLineRow(sku = "", quantity = "1") {
      const row = document.createElement("div");
      row.className = "line-row";
      row.innerHTML =
        '<select class="line-sku">' + inventoryOptionsHtml(sku) + '</select>' +
        '<input type="number" class="line-quantity" min="1" step="1" value="' + escapeHtml(quantity) + '">' +
        '<button type="button" class="danger line-remove">Remove</button>';

      row.querySelector(".line-remove").addEventListener("click", () => {
        row.remove();
        if (lineItemsContainer.children.length === 0) {
          addLineRow();
        }
      });

      lineItemsContainer.appendChild(row);
    }

    function addLineRow(sku = "", quantity = "1") {
      renderLineRow(sku, quantity);
    }

    function fillLineRows(lines) {
      lineItemsContainer.innerHTML = "";
      for (const line of lines) {
        addLineRow(line.sku, String(line.quantity));
      }
      if (lineItemsContainer.children.length === 0) {
        addLineRow();
      }
    }

    function currentLineDrafts() {
      return Array.from(lineItemsContainer.querySelectorAll(".line-row")).map((row) => ({
        sku: row.querySelector(".line-sku").value,
        quantity: row.querySelector(".line-quantity").value || "1",
      }));
    }

    function parseLines() {
      const rows = Array.from(lineItemsContainer.querySelectorAll(".line-row"));
      const lines = rows
        .map((row) => ({
          sku: row.querySelector(".line-sku").value.trim(),
          quantityRaw: row.querySelector(".line-quantity").value.trim(),
        }))
        .filter((line) => line.sku || line.quantityRaw);

      if (lines.length === 0) {
        throw new Error("Add at least one order line.");
      }

      return lines.map((line, index) => {
        if (!line.sku) {
          throw new Error("Line " + (index + 1) + " needs a SKU.");
        }

        const quantity = Number(line.quantityRaw);
        if (!Number.isInteger(quantity) || quantity <= 0) {
          throw new Error("Line " + (index + 1) + " must use a whole quantity greater than zero.");
        }

        return { sku: line.sku, quantity };
      });
    }

    function syncEditorState() {
      if (state.editingOrderId === null) {
        formTitle.textContent = "New Order";
        submitOrderButton.textContent = "Add Order";
      } else {
        formTitle.textContent = "Edit Order";
        submitOrderButton.textContent = "Update Order";
      }
    }

    function clearEditor() {
      state.editingOrderId = null;
      orderIdInput.value = "";
      customerIdInput.value = "";
      statusInput.value = "created";
      fillLineRows([]);
      syncEditorState();
    }

    function startEdit(orderId) {
      const order = state.orders.find((item) => item.id === orderId);
      if (!order) {
        showBanner("error", "Order " + orderId + " was not found.");
        return;
      }

      state.editingOrderId = order.id;
      orderIdInput.value = order.id;
      customerIdInput.value = order.customer_id;
      statusInput.value = order.status;
      fillLineRows(order.lines);
      syncEditorState();
      clearBanner();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    async function deleteOrder(orderId) {
      if (!window.confirm("Delete order " + orderId + "? Inventory will be restored.")) {
        return;
      }

      const response = await fetch("/orders/" + orderId, { method: "DELETE" });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Delete failed." }));
        showBanner("error", error.detail || "Delete failed.");
        return;
      }

      if (state.editingOrderId === orderId) {
        clearEditor();
      }
      showBanner("success", "Order " + orderId + " deleted.");
      await loadData();
    }

    function renderOrders() {
      if (state.orders.length === 0) {
        ordersContainer.innerHTML = '<div class="empty">No orders found.</div>';
        return;
      }

      const rows = state.orders.map((order) => {
        const lines = order.lines
          .map((line) => escapeHtml(line.sku) + " x " + line.quantity + " (" + formatMoney(line.line_total_cents) + ")")
          .join("<br>");

        return "<tr>" +
          "<td>" + order.id + "</td>" +
          "<td>" + escapeHtml(order.customer_id) + "</td>" +
          "<td><span class=\\"status\\">" + escapeHtml(order.status) + "</span></td>" +
          "<td>" + formatMoney(order.total_amount_cents) + "</td>" +
          "<td>" + lines + "</td>" +
          "<td>" + new Date(order.created_at).toLocaleString() + "</td>" +
          "<td><div class=\\"actions\\">" +
          "<button class=\\"secondary\\" type=\\"button\\" data-edit-order=\\"" + order.id + "\\">Edit</button>" +
          "<button class=\\"danger\\" type=\\"button\\" data-delete-order=\\"" + order.id + "\\">Delete</button>" +
          "</div></td>" +
          "</tr>";
      }).join("");

      ordersContainer.innerHTML =
        "<div class=\\"table-wrap\\"><table>" +
        "<thead><tr><th>ID</th><th>Customer</th><th>Status</th><th>Total</th><th>Lines</th><th>Created</th><th>Actions</th></tr></thead>" +
        "<tbody>" + rows + "</tbody>" +
        "</table></div>";

      for (const button of document.querySelectorAll("[data-edit-order]")) {
        button.addEventListener("click", () => startEdit(Number(button.dataset.editOrder)));
      }
      for (const button of document.querySelectorAll("[data-delete-order]")) {
        button.addEventListener("click", () => deleteOrder(Number(button.dataset.deleteOrder)));
      }
    }

    function renderInventory() {
      if (state.inventory.length === 0) {
        inventoryContainer.innerHTML = '<div class="empty">No inventory items found yet. Add one below to enable the order dropdown.</div>';
        return;
      }

      const rows = state.inventory.map((item) =>
        "<tr>" +
        "<td>" + escapeHtml(item.sku) + "</td>" +
        "<td>" + escapeHtml(item.name) + "</td>" +
        "<td>" + item.stock + "</td>" +
        "<td>" + formatMoney(item.unit_price_cents) + "</td>" +
        "</tr>"
      ).join("");

      inventoryContainer.innerHTML =
        "<div class=\\"table-wrap\\"><table>" +
        "<thead><tr><th>SKU</th><th>Name</th><th>Stock</th><th>Unit Price</th></tr></thead>" +
        "<tbody>" + rows + "</tbody>" +
        "</table></div>";
    }

    async function loadData() {
      const drafts = currentLineDrafts();
      const [ordersResponse, inventoryResponse] = await Promise.all([
        fetch("/orders"),
        fetch("/inventory-items")
      ]);

      state.orders = await ordersResponse.json();
      state.inventory = await inventoryResponse.json();

      renderOrders();
      renderInventory();

      if (state.editingOrderId !== null) {
        const order = state.orders.find((item) => item.id === state.editingOrderId);
        if (order) {
          startEdit(order.id);
        } else {
          clearEditor();
        }
      } else {
        fillLineRows(drafts);
      }
    }

    orderForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      let payload;
      try {
        payload = {
          customer_id: customerIdInput.value.trim(),
          status: statusInput.value.trim(),
          lines: parseLines(),
        };
      } catch (error) {
        showBanner("error", error.message);
        return;
      }

      const isEditing = state.editingOrderId !== null;
      const response = await fetch(isEditing ? "/orders/" + state.editingOrderId : "/orders", {
        method: isEditing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          isEditing
            ? payload
            : {
                customer_id: payload.customer_id,
                lines: payload.lines,
              }
        ),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Update failed." }));
        showBanner("error", error.detail || "Update failed.");
        return;
      }

      const savedOrder = await response.json();
      showBanner("success", "Order " + savedOrder.id + (isEditing ? " updated." : " created."));
      if (!isEditing) {
        clearEditor();
      }
      await loadData();
    });

    cancelEditButton.addEventListener("click", () => {
      clearEditor();
      clearBanner();
    });

    newOrderButton.addEventListener("click", () => {
      clearEditor();
      clearBanner();
      customerIdInput.focus();
    });

    addLineButton.addEventListener("click", () => {
      addLineRow();
    });

    inventoryForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const payload = {
        sku: inventorySkuInput.value.trim(),
        name: inventoryNameInput.value.trim(),
        stock: Number(inventoryStockInput.value),
        unit_price_cents: Number(inventoryPriceInput.value),
      };

      const response = await fetch("/inventory-items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Inventory add failed." }));
        showBanner("error", error.detail || "Inventory add failed.");
        return;
      }

      const item = await response.json();
      inventoryForm.reset();
      inventoryStockInput.value = "1";
      showBanner("success", "Inventory item " + item.name + " added.");
      await loadData();

      const firstEmptySku = lineItemsContainer.querySelector(".line-sku");
      if (firstEmptySku && !firstEmptySku.value) {
        firstEmptySku.value = item.sku;
      }
    });

    clearEditor();
    loadData().catch(() => {
      showBanner("error", "Could not load order data.");
      ordersContainer.innerHTML = '<div class="empty">Could not load orders.</div>';
      inventoryContainer.innerHTML = '<div class="empty">Could not load inventory.</div>';
    });
  </script>
</body>
</html>
"""
