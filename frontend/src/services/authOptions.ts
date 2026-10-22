
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import { adminDb } from "@/services/firebaseAdmin";

export const authOptions: NextAuthOptions = {
  debug: process.env.NODE_ENV === "development",
  session: {
    strategy: "jwt",
  },

  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    }),

    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "E-mail", type: "email" },
        code: { label: "Código", type: "text" },
      },

      async authorize(credentials) {
        const email = credentials?.email?.trim().toLowerCase();
        const code = credentials?.code?.trim();

        if (!email || !code) return null;

        const userRef = adminDb.collection("users").doc(email);
        const userDoc = await userRef.get();

        if (!userDoc.exists) return null;

        const codeRef = adminDb.collection("authCodes").doc(email);

        // Valida e consome o código atomicamente, evitando reutilização
        // em solicitações simultâneas.
        const validCode = await adminDb.runTransaction(async (tx) => {
          const codeDoc = await tx.get(codeRef);

          if (!codeDoc.exists) return false;

          const data = codeDoc.data();
          const createdAt = Number(data?.createdAt);
          const now = Date.now();

          const valid =
            data?.code === code &&
            Number.isFinite(createdAt) &&
            createdAt <= now &&
            now - createdAt < 5 * 60 * 1000;

          if (valid) {
            tx.delete(codeRef);
          }

          return valid;
        });

        if (!validCode) return null;

        const userData = userDoc.data();

        return {
          id: email,
          email,
          name:
            userData?.username ||
            userData?.displayName ||
            email,
        };
      },
    }),
  ],

  pages: {
    signIn: "/auth/login",
    newUser: "/auth/register",
  },

  secret: process.env.NEXTAUTH_SECRET,
};
