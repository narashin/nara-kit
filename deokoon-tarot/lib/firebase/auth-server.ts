import type { DecodedIdToken } from "firebase-admin/auth";
import { getAdminAuth } from "./admin";

// Authorization 헤더의 Firebase ID Token 검증. 실패 시 null.
export async function verifyIdToken(
  authHeader: string | null,
): Promise<DecodedIdToken | null> {
  if (!authHeader?.startsWith("Bearer ")) return null;
  const token = authHeader.slice("Bearer ".length).trim();
  if (!token) return null;
  try {
    return await getAdminAuth().verifyIdToken(token);
  } catch {
    return null;
  }
}
