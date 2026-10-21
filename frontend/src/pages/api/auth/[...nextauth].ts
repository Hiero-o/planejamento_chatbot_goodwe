import NextAuth from "next-auth/next";
import { getAuth } from "firebase/auth";
import { signInWithEmailAndPassword } from "firebase/auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { db } from "@/services/firebaseConnection";
import { doc, getDoc } from "firebase/firestore";
import GoogleProvider from 'next-auth/providers/google'

export default NextAuth({
    debug: true,
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID as string,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
        }),
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "email" },
                code: { label: "Code", type: "text" }
            },
            async authorize(credentials) {
                if (!credentials || !credentials.email || !credentials.code) {
                    throw new Error("Faltando email ou código.")
                }

                const userRef = doc(db, 'users', credentials.email)
                const userDoc = await getDoc(userRef)

                if (!userDoc.exists()) {
                    throw new Error("Este e-mail não está registrado.");
                }

                const authCodeRef = doc(db, 'authCodes', credentials.email)
                const authCodeDoc = await getDoc(authCodeRef)

                if (authCodeDoc.exists()) {
                    const storeData = authCodeDoc.data()
                    const now = Date.now()

                    if (storeData.code === credentials.code && now - storeData.createdAt < 300000) {
                        const userRef = doc(db, 'users', credentials.email)
                        const userDoc = await getDoc(userRef)

                        if (userDoc.exists()) {
                            const userData = userDoc.data()
                            return {
                                id: credentials.email,
                                email: credentials.email,
                                name: userData.username || userData.displayName || credentials.email,
                            }
                        } else {
                            throw new Error("Código inválido ou expirado.")
                        }
                    } else {
                        throw new Error("Código inválido ou expirado.")
                    }
                }
                return null
            }
        })
    ],
    pages: {
        signIn: '/auth/login',
        newUser: '/auth/register'
    },
    secret: process.env.JWT_SECRET as string
})