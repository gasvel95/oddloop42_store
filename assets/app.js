const buttons = document.querySelectorAll('[data-filter]');
const products = document.querySelectorAll('[data-category]');
buttons.forEach(button => button.addEventListener('click', () => {
  buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  let count = 0;
  products.forEach(product => {
    product.hidden = button.dataset.filter !== 'All' && product.dataset.category !== button.dataset.filter;
    if (!product.hidden) count++;
  });
  document.querySelector('#count').textContent = `${count} ${count === 1 ? 'selected design' : 'selected designs'}`;
}));
