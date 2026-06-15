const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function lookupOrder(orderId) {
  const res = await fetch(`${API}/api/orders/lookup?order_id=${encodeURIComponent(orderId)}`);
  if (!res.ok) throw new Error('Server error');
  return res.json();
}

export async function getBusinesses() {
  const res = await fetch(`${API}/api/businesses`);
  if (!res.ok) throw new Error('Server error');
  return res.json();
}

export async function submitReview(data) {
  const fd = new FormData();
  fd.append('business_id', data.businessId);
  fd.append('bill_id', data.billId);
  fd.append('review_text', data.reviewText);
  fd.append('has_media', data.images.length > 0 ? 'true' : 'false');
  data.images.forEach(f => fd.append('images', f));

  const res = await fetch(`${API}/api/review`, { method: 'POST', body: fd });
  if (!res.ok) throw new Error(`Server error ${res.status}`);
  return res.json();
}

export async function getReviews(limit = 50) {
  const res = await fetch(`${API}/api/reviews?limit=${limit}`);
  if (!res.ok) throw new Error('Server error');
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API}/`);
  return res.ok;
}
