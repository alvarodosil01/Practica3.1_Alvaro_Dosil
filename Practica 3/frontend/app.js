/* Cliente web de P2_2. Las llamadas HTTP están centralizadas en api().
   No importa clases, servicios ni código Python del servidor. */
'use strict';
const $ = (selector) => document.querySelector(selector);
const money = (value) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
const state = { baseUrl: '', connected: false, products: [], users: [], historyClient: '' };
let noticeTimer;
let connectionGeneration = 0;

function node(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}

function notify(message, error = false) {
  clearTimeout(noticeTimer);
  const box = $('#notification');
  box.textContent = message;
  box.classList.toggle('error', error);
  box.hidden = false;
  noticeTimer = setTimeout(() => { box.hidden = true; }, error ? 12000 : 6500);
}

function setConnection(connected, label) {
  state.connected = connected;
  const indicator = $('#connection-status');
  indicator.textContent = label;
  indicator.className = 'connection' + (connected ? ' online' : label === 'Sin conexión' ? ' error' : '');
  document.querySelectorAll('[data-needs-server]').forEach((button) => { button.disabled = !connected; });
}

function parseUrl(value) {
  const url = new URL(value.trim());
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error('Introduce una dirección HTTP válida, por ejemplo http://127.0.0.1:8000.');
  }
  return url.href.replace(/\/+$/, '');
}

function explainError(detail) {
  if (Array.isArray(detail)) return detail.map((error) => `${(error.loc || []).slice(1).join(' · ')}: ${error.msg}`).join('. ');
  return typeof detail === 'string' ? detail : 'El servidor no pudo completar la operación.';
}

// Único punto de comunicación: fetch envía JSON y comprueba estado y respuesta.
async function api(path, { method = 'GET', data, expected = 200, baseUrl = state.baseUrl } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(baseUrl + path, {
      method, signal: controller.signal,
      headers: data === undefined ? {} : { 'Content-Type': 'application/json' },
      body: data === undefined ? undefined : JSON.stringify(data),
    });
    const body = response.status === 204 ? null : await response.json();
    if (response.status !== expected) throw new Error(explainError(body?.detail) + ` (HTTP ${response.status})`);
    return body;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('El servidor tarda demasiado en responder. Revisa la dirección y la conexión.');
    if (error instanceof TypeError) throw new Error('No se pudo conectar con la tienda. Comprueba que FastAPI está iniciado y que la dirección es correcta.');
    if (error instanceof SyntaxError) throw new Error('El servidor no devolvió JSON válido. Comprueba la dirección de la API.');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function categoryName(type) { return ({ generico: 'Genérico', electronico: 'Electrónico', ropa: 'Ropa' })[type] || type; }

function productIcon(type) {
  // Los dibujos son constantes; los textos del servidor se insertan con textContent.
  const paths = {
    generico: '<path d="m8 15 16-8 16 8v21l-16 8-16-8V15Z"/><path d="m8 15 16 8 16-8M24 23v21M16 11l16 8"/>',
    electronico: '<path d="M9 28v-8a15 15 0 0 1 30 0v8"/><rect x="6" y="24" width="8" height="14" rx="3"/><rect x="34" y="24" width="8" height="14" rx="3"/><path d="M38 38c0 4-5 5-10 5"/>',
    ropa: '<path d="m16 8-11 8 6 9 5-3v21h16V22l5 3 6-9-11-8c-2 5-14 5-16 0Z"/>',
  };
  const visual = node('div', 'product-visual');
  visual.dataset.type = type;
  visual.setAttribute('aria-hidden', 'true');
  visual.innerHTML = `<svg viewBox="0 0 48 48">${paths[type] || paths.generico}</svg>`;
  return visual;
}

function renderProducts() {
  const list = $('#product-list');
  list.replaceChildren();
  $('#product-count').textContent = state.products.length;
  $('#catalog-caption').textContent = state.connected ? `${state.products.length} productos · ${state.products.reduce((n, p) => n + p.stock, 0)} unidades disponibles` : 'Conecta para ver tu catálogo.';
  if (!state.products.length) list.append(node('div', 'empty', state.connected ? 'Tu catálogo está listo para empezar. Añade tu primer producto.' : 'Conecta con el servidor para consultar los productos.'));
  for (const product of state.products) {
    const card = node('article', 'card product-card');
    card.dataset.productId = product.id;
    let details = 'Producto de la tienda';
    if (product.tipo === 'electronico') details = `${product.meses_garantia} meses de garantía`;
    if (product.tipo === 'ropa') details = `Talla ${product.talla} · ${product.color}`;
    const bottom = node('div', 'product-bottom');
    bottom.append(node('strong', 'price', money(product.precio)), node('span', 'stock' + (product.stock ? '' : ' zero'), product.stock ? `${product.stock} disponibles` : 'Sin stock'));
    card.append(productIcon(product.tipo), node('div', 'category', categoryName(product.tipo)), node('h3', '', product.nombre), node('p', 'product-details', details), bottom);
    list.append(card);
  }
}

function fillOptions(select, choices, prompt, previous = select.value) {
  select.replaceChildren(new Option(prompt, ''));
  for (const choice of choices) select.add(new Option(choice.label, choice.value));
  select.value = choices.some((choice) => choice.value === previous) ? previous : '';
}

function renderUsers() {
  const list = $('#user-list');
  list.replaceChildren();
  $('#user-count').textContent = state.users.length;
  if (!state.users.length) list.append(node('div', 'empty', state.connected ? 'Todavía no hay usuarios. Crea el primer cliente de tu tienda.' : 'Conecta con el servidor para consultar los usuarios.'));
  for (const user of state.users) {
    const card = node('article', 'card user-card');
    const info = node('div', 'user-info');
    info.append(node('h3', '', user.nombre), node('p', '', user.email));
    card.append(node('div', 'avatar', user.nombre.slice(0, 1).toUpperCase()), info, node('span', 'role', user.es_admin ? 'Administrador' : 'Cliente'));
    list.append(card);
  }
  const clients = state.users.filter((user) => !user.es_admin).map((user) => ({ label: `${user.nombre} · ${user.email}`, value: user.id }));
  fillOptions($('#order-client'), clients, clients.length ? 'Selecciona un cliente' : 'Crea primero un cliente');
  fillOptions($('#history-client'), clients, clients.length ? 'Selecciona un cliente' : 'Crea primero un cliente');
}

function fillProductChoices() {
  const products = state.products.filter((product) => product.stock > 0).map((product) => ({ label: `${product.nombre} · ${money(product.precio)} · stock ${product.stock}`, value: product.id }));
  document.querySelectorAll('.line-product').forEach((select) => fillOptions(select, products, products.length ? 'Selecciona un producto' : 'Añade productos con stock'));
  updateTotal();
}

function renderAll() { renderProducts(); renderUsers(); fillProductChoices(); }

async function refresh() {
  const generation = connectionGeneration;
  const [products, users] = await Promise.all([api('/productos'), api('/usuarios')]);
  if (generation !== connectionGeneration) return;
  state.products = products;
  state.users = users;
  renderAll();
}

async function connect() {
  const generation = ++connectionGeneration;
  const button = $('#connect-button');
  button.disabled = true;
  setConnection(false, 'Conectando…');
  state.products = [];
  state.users = [];
  state.historyClient = '';
  $('#history-list').replaceChildren(node('div', 'empty', 'Selecciona un cliente para consultar sus pedidos.'));
  renderAll();
  try {
    const baseUrl = parseUrl($('#server-url').value);
    const [products, users] = await Promise.all([api('/productos', { baseUrl }), api('/usuarios', { baseUrl })]);
    if (generation !== connectionGeneration) return;
    state.baseUrl = baseUrl;
    state.products = products;
    state.users = users;
    try { localStorage.setItem('alvaro-api-url', baseUrl); } catch (_) { /* El navegador puede impedir el almacenamiento local. */ }
    $('#docs-link').href = baseUrl + '/docs';
    setConnection(true, 'Conectado');
    renderAll();
    notify('Conexión lista. La tienda está actualizada.');
  } catch (error) {
    setConnection(false, 'Sin conexión');
    notify(error.message, true);
  } finally { button.disabled = false; }
}

function productCategory() {
  const type = $('#product-type').value;
  for (const [id, enabled] of [['electronic-fields', type === 'electronico'], ['clothing-fields', type === 'ropa']]) {
    const fieldset = $('#' + id);
    fieldset.hidden = !enabled;
    fieldset.disabled = !enabled;
  }
}

function userCategory() {
  $('#user-address').required = $('#user-type').value === 'cliente';
}

function addLine() {
  const row = node('div', 'order-line');
  const productLabel = node('label', '', 'Producto');
  const select = node('select', 'line-product');
  select.required = true;
  productLabel.append(select);
  const quantityLabel = node('label', '', 'Cantidad');
  const quantity = node('input', 'line-quantity');
  Object.assign(quantity, { type: 'number', min: '1', step: '1', value: '1', required: true });
  quantityLabel.append(quantity);
  const remove = node('button', 'remove-line', '×');
  remove.type = 'button';
  remove.setAttribute('aria-label', 'Quitar línea de pedido');
  remove.addEventListener('click', () => {
    if ($('#order-lines').children.length === 1) { select.value = ''; quantity.value = '1'; }
    else row.remove();
    updateTotal();
  });
  row.append(productLabel, quantityLabel, remove);
  $('#order-lines').append(row);
  fillProductChoices();
}

function updateTotal() {
  let total = 0;
  document.querySelectorAll('.order-line').forEach((row) => {
    const product = state.products.find((p) => p.id === row.querySelector('select').value);
    const quantity = Number(row.querySelector('input').value);
    if (product && Number.isFinite(quantity) && quantity > 0) total += product.precio * quantity;
  });
  $('#order-total').textContent = money(total);
}

async function loadHistory(clientId) {
  const generation = connectionGeneration;
  const orders = await api(`/usuarios/${encodeURIComponent(clientId)}/pedidos`);
  if (generation !== connectionGeneration || $('#history-client').value !== clientId) return;
  state.historyClient = clientId;
  const list = $('#history-list');
  list.replaceChildren();
  if (!orders.length) list.append(node('div', 'empty', 'Este cliente todavía no ha realizado pedidos.'));
  for (const order of [...orders].reverse()) {
    const card = node('article', 'card history-card');
    const header = node('div', 'history-top');
    const meta = node('div');
    meta.append(node('h4', '', `Pedido ${order.id.slice(0, 8)}`), node('p', '', new Date(order.fecha).toLocaleString('es-ES')));
    header.append(meta, node('strong', '', money(order.total)));
    card.append(header);
    for (const item of order.items) {
      const line = node('div', 'history-item');
      line.append(node('span', '', `${item.cantidad} × ${item.nombre}`), node('span', '', money(item.subtotal)));
      card.append(line);
    }
    list.append(card);
  }
}

function submit(formSelector, action) {
  $(formSelector).addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!state.connected) return notify('Conecta con el servidor para continuar.', true);
    const button = event.currentTarget.querySelector('[type=submit]');
    button.disabled = true;
    try { await action(event.currentTarget); }
    catch (error) { notify(error.message, true); }
    finally { button.disabled = !state.connected; }
  });
}

$('#server-form').addEventListener('submit', (event) => { event.preventDefault(); connect(); });
$('#refresh-button').addEventListener('click', async () => {
  if (!state.connected) return connect();
  try {
    await refresh();
    if (state.historyClient && $('#history-client').value === state.historyClient) await loadHistory(state.historyClient);
    notify('Catálogo y usuarios actualizados.');
  } catch (error) { notify(error.message, true); }
});
document.querySelectorAll('[data-tab]').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('[data-tab]').forEach((tab) => tab.removeAttribute('aria-current'));
  button.setAttribute('aria-current', 'page');
  document.querySelectorAll('.panel').forEach((panel) => { panel.hidden = panel.id !== 'panel-' + button.dataset.tab; });
}));
$('#product-type').addEventListener('change', productCategory);
$('#user-type').addEventListener('change', userCategory);
$('#add-line').addEventListener('click', addLine);
$('#order-lines').addEventListener('input', updateTotal);
$('#order-lines').addEventListener('change', updateTotal);
$('#history-client').addEventListener('change', () => {
  state.historyClient = '';
  $('#history-list').replaceChildren(node('div', 'empty', 'Pulsa Consultar para cargar los pedidos de este cliente.'));
});

submit('#product-form', async (form) => {
  const values = Object.fromEntries(new FormData(form));
  const data = { tipo: values.tipo, nombre: values.nombre, precio: Number(values.precio), stock: Number(values.stock) };
  if (values.tipo === 'electronico') data.meses_garantia = Number(values.meses_garantia);
  if (values.tipo === 'ropa') Object.assign(data, { talla: values.talla, color: values.color });
  await api('/productos', { method: 'POST', data, expected: 201 });
  form.reset(); productCategory();
  try { await refresh(); notify('Producto añadido al catálogo.'); }
  catch (error) { notify('Producto creado. No se pudo actualizar el listado: ' + error.message, true); }
});

submit('#user-form', async (form) => {
  const data = Object.fromEntries(new FormData(form));
  if (!data.direccion?.trim()) delete data.direccion;
  const user = await api('/usuarios', { method: 'POST', data, expected: 201 });
  form.reset(); userCategory();
  try {
    await refresh();
    if (!user.es_admin) { $('#order-client').value = user.id; $('#history-client').value = user.id; }
    notify('Usuario creado. Ya puedes preparar su primer pedido.');
  } catch (error) { notify('Usuario creado. No se pudo actualizar el listado: ' + error.message, true); }
});

submit('#order-form', async (form) => {
  const clientId = $('#order-client').value;
  const items = [...document.querySelectorAll('.order-line')].map((row) => ({ producto_id: row.querySelector('select').value, cantidad: Number(row.querySelector('input').value) }));
  const order = await api('/pedidos', { method: 'POST', expected: 201, data: { cliente_id: clientId, items } });
  $('#order-lines').replaceChildren(); addLine();
  try {
    await refresh();
    $('#history-client').value = clientId;
    await loadHistory(clientId);
    notify(`Pedido confirmado. Total: ${money(order.total)}.`);
  } catch (error) { notify('Pedido creado. No se pudo actualizar la vista: ' + error.message, true); }
});

submit('#history-form', async () => { await loadHistory($('#history-client').value); });

let initialUrl = 'http://127.0.0.1:8000';
try { initialUrl = localStorage.getItem('alvaro-api-url') || initialUrl; } catch (_) { /* Preferencia opcional. */ }
$('#server-url').value = initialUrl;
productCategory(); userCategory(); addLine(); renderAll();
connect();
