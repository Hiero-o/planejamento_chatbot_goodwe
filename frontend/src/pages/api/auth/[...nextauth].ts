
import NextAuth from "next-auth/next";
import { authOptions } from "@/services/authOptions";

export default NextAuth(authOptions);
