import { cert, getApps, initializeApp, type App } from "firebase-admin/app";
import { getAuth, type Auth } from "firebase-admin/auth";
import { getFirestore, type Firestore } from "firebase-admin/firestore";

type AdminBundle = { app: App; auth: Auth; db: Firestore };

let cached: AdminBundle | null = null;

// Lazy init — import 시점에 throw하지 않도록(placeholder env로도 빌드/부팅 가능).
function init(): AdminBundle {
  const existing = getApps()[0];
  if (existing) {
    return { app: existing, auth: getAuth(existing), db: getFirestore(existing) };
  }

  const projectId = process.env.FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n");

  if (!projectId || !clientEmail || !privateKey) {
    throw new Error(
      "Firebase Admin env가 없습니다 (FIREBASE_PROJECT_ID / FIREBASE_CLIENT_EMAIL / FIREBASE_PRIVATE_KEY)",
    );
  }

  const app = initializeApp({ credential: cert({ projectId, clientEmail, privateKey }) });
  return { app, auth: getAuth(app), db: getFirestore(app) };
}

function admin(): AdminBundle {
  if (!cached) cached = init();
  return cached;
}

export function getAdminAuth(): Auth {
  return admin().auth;
}

export function getAdminDb(): Firestore {
  return admin().db;
}
