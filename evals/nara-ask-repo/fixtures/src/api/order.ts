import type { Order } from "../types";

interface OrderResponse {
  id: string;
  promo: { rate: number } | null;
}

export function toOrder(res: OrderResponse): Order {
  const rate = res.promo ? res.promo.rate * 100 : 0;
  return { id: res.id, discountRate: Math.round(rate) };
}
