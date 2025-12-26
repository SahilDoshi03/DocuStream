"use client";

import { ChatInterface } from "../../../components/ChatInterface";
import { useParams } from "next/navigation";

export default function ChatPage() {
    const params = useParams();
    const chatId = params.chatId as string;

    return (
        <div className="h-full bg-zinc-50/50 dark:bg-black">
            <ChatInterface chatId={chatId} />
        </div>
    );
}
