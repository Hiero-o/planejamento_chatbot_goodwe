import "server-only";

import {
  applicationDefault,
  getApp,
  getApps,
  initializeApp,
} from "firebase-admin/app";

import { getFirestore } from "firebase-admin/firestore";

const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;

if (!projectId) {
  throw new Error(
    "A variável NEXT_PUBLIC_FIREBASE_PROJECT_ID não foi configurada."
  );
}

const firebaseAdminApp =
  getApps().length > 0
    ? getApp()
    : initializeApp({
        credential: applicationDefault(),
        projectId,
      });

export const adminDb = getFirestore(firebaseAdminApp);