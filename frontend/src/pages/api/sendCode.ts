import nodemailer from 'nodemailer';
import { db } from '@/services/firebaseConnection';
import { doc, setDoc } from 'firebase/firestore';

export default async function handler(req: any, res: any) {
    if (req.method === 'POST') {
        const { email } = req.body
        const code = Math.floor(1000 + Math.random() * 9000).toString()

        try {
            const transporter = nodemailer.createTransport({
                service: 'gmail',
                auth: {
                    user: process.env.EMAIL_USER,
                    pass: process.env.EMAIL_PASS,
                }
            })

            const mailOptions = {
                from: process.env.EMAIL_USER,
                to: email,
                subject: 'Seu código de acesso',
                html: `
                    <html>
                        <body style="font-family: "Inter", serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                            <p>${code}</p>
                        </body>
                    </html>
                `
            }

            await transporter.sendMail(mailOptions)

            await setDoc(doc(db, 'authCodes', email), {
                code,
                createdAt: Date.now()
            })

            return res.status(200).json({ message: 'Código enviado com sucesso.' })
        } catch (error) {
            console.error('Erro ao enviar código', error)
            return res.status(500).json({ error: 'Erro ao enviar código' })
        }
    } else {
        return res.status(405).json({ error: 'Método não permitido' })
    }
}