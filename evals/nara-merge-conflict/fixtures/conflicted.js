export function total(items) {
<<<<<<< HEAD
  // ours: price * quantity model
  return items.reduce((sum, i) => sum + i.price * i.qty, 0);
=======
  // theirs: precomputed amount model
  return items.reduce((sum, i) => sum + i.amount, 0);
>>>>>>> feature/pricing
}
