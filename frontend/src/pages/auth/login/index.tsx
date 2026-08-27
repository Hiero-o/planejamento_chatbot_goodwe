import { useState } from "react"
import { useRouter } from "next/router"
import { toast } from "@/components/ui/toast"
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { db } from '@/services/firebaseConnection';
import { FormEvent } from "react";
import { signIn } from 'next-auth/react'

export default function Login() {
    const [email, setEmail] = useState('')
    const [codeSent, setCodeSent] = useState(false)
    const [code, setCode] = useState('')
    const [inputColor, setInputColor] = useState('')
    const router = useRouter()
    const [loading, setLoading] = useState(false)

    async function handleRequestCode(event: FormEvent) {
        event.preventDefault()

        setLoading(true)

        const userRef = doc(db, 'users', email)
        const userDoc = await getDoc(userRef)

        if (!userDoc.exists()) {
            toast.add({
                title: "E-mail não encontrado",
                description: "Não localizamos uma conta com este e-mail.",
            })
            setLoading(false)
            router.push("/auth/register")
            return
        }

        const response = await fetch('/api/sendCode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        })

        if (response.ok) {
            setCodeSent(true)
            toast.add({
                title: "Código enviado",
                description: "Verifique sua caixa de entrada e informe o código recebido.",
            })
        } else {
            toast.add({
                title: "Falha no envio",
                description: "Não foi possível enviar o código. Tente novamente em instantes.",
            })
        }

        setLoading(false)
    }

    async function handleLoginUser(event: FormEvent) {
        event.preventDefault()

        setLoading(true)

        const result = await signIn('credentials', {
            redirect: false,
            email,
            code
        })

        console.log(result)

        if (!result?.error) {
            setInputColor('#7bd4641e')
            router.push('/dashboard')
            setLoading(false)
        } else {
            console.error(result.error)
            toast.add({
                title: "Código inválido",
                description: "O código informado é inválido ou expirou. Solicite um novo código.",
            })
            setInputColor('#cd35353f')
        }

        setLoading(false)
    }

    return (
        <>
            <main className="flex items-center justify-center flex-col min-h-[100vh]">
                <form className="flex items-center justify-center flex-col w-[300px]" onSubmit={codeSent ? handleLoginUser : handleRequestCode}>
                    <img src="/icon.png" alt="" className="h-[35px] w-[20px] mb-[10px]" />
                    <h1 className="text-[30px] font-bold mb-[10px]">Bem-vindo</h1>
                    <p className="text-center mb-[15px] text-[14px] text-[#b3b3b3]">Entre com seu e-mail para receber um código de acesso</p>
                    <input value={email} onChange={(event) => setEmail(event.target.value)} required disabled={codeSent} type="text" placeholder="seu@email.com" className="mb-[10px] w-full outline-none font-normal rounded-[8px] py-[6px] px-[6px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] transition-[0.3s] focus:border-[#47474b]" />
                    {codeSent && (
                        <input
                            type="text" placeholder='Digite o código recebido'
                            value={code} onChange={(event) => setCode(event.target.value)} required
                            className="mb-[10px] w-full outline-none font-normal rounded-[8px] py-[6px] px-[6px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] transition-[0.3s] focus:border-[#47474b]"
                            maxLength={4}
                        />
                    )}
                    <button disabled={loading} type='submit' style={loading ? { backgroundColor: '#89920d', } : {}} className="mb-[15px] w-full rounded-[8px] py-[6px] px-[15px] text-[14px] bg-[#ECFF00] text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#89920d]">
                        {loading ? (
                            <>
                                Carregando
                            </>
                        ) : codeSent ? 'Entrar' : 'Enviar código'}
                    </button>
                    <div className="flex items-center justify-between w-full flex-row mb-[15px] gap-[15px]">
                        <div className="w-full p-[0.5px] h-[0.5px] bg-[#5f5f5f]"></div>
                        <p className="leading-[1.2] text-[#5f5f5f]">ou</p>
                        <div className="w-full p-[0.5px] h-[0.5px] bg-[#5f5f5f]"></div>
                    </div>
                    <button onClick={() => signIn('google')} type="button" className="w-full flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A]">
                        <img src="/icongoogle.webp" alt="Google icon" className="h-[18px] w-[18px] mr-[15px]" />
                        Continuar com Google
                    </button>
                </form>
            </main>
        </>
    )
}