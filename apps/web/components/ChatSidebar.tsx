"use client";

import Link from "next/link";
import { Plus, MessageSquare, Settings, FileText, Trash2 } from "lucide-react";
import { clsx } from "clsx";
import { useQuery, useMutation } from "@tanstack/react-query";

// Mock data removed


export function ChatSidebar() {
    const { data: chats, refetch } = useQuery({
        queryKey: ["chats"],
        queryFn: async () => {
            const res = await fetch("/api/chats");
            if (!res.ok) throw new Error("Failed to fetch chats");
            return res.json();
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (chatId: string) => {
            const res = await fetch(`/api/chats/${chatId}`, { method: "DELETE" });
            if (!res.ok) throw new Error("Failed to delete chat");
            return res.json();
        },
        onSuccess: () => {
            refetch();
        }
    });

    const handleDelete = (e: React.MouseEvent, chatId: string) => {
        e.preventDefault();
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this chat?")) {
            deleteMutation.mutate(chatId);
        }
    };

    return (
        <div className="flex h-screen flex-col justify-between border-r bg-zinc-50 dark:bg-zinc-900 w-64 flex-shrink-0">
            <div className="px-4 py-4 flex flex-col h-full">
                {/* Header / New Chat */}
                <div className="mb-6">
                    <Link
                        href="/"
                        className="flex items-center gap-2 px-2 mb-6"
                    >
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
                            <FileText className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
                            DocuStream
                        </span>
                    </Link>

                    <Link
                        href="/"
                        className="flex items-center gap-2 w-full rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-black px-3 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors shadow-sm"
                    >
                        <Plus className="h-4 w-4" />
                        New Chat
                    </Link>
                </div>

                {/* History */}
                <div className="flex-1 overflow-y-auto -mx-2 px-2">
                    <div className="text-xs font-semibold text-zinc-400 mb-3 px-2 uppercase tracking-wider">
                        Recent
                    </div>
                    <nav className="flex flex-col gap-1">
                        {chats?.map((chat: any) => (
                            <Link
                                key={chat.id}
                                href={`/chat/${chat.id}`}
                                className="group flex items-center justify-between rounded-md px-3 py-2 text-sm text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200/50 dark:hover:bg-zinc-800 transition-colors"
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <MessageSquare className="h-4 w-4 flex-shrink-0" />
                                    <span className="truncate">{chat.title || "New Chat"}</span>
                                </div>
                                <button
                                    onClick={(e) => handleDelete(e, chat.id)}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-opacity"
                                >
                                    <Trash2 className="h-3 w-3" />
                                </button>
                            </Link>
                        ))}
                    </nav>
                </div>

                {/* Footer */}
                <div className="mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-800">
                    <Link
                        href="/settings"
                        className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 transition-colors"
                    >
                        <Settings className="h-4 w-4" />
                        Settings
                    </Link>
                </div>
            </div>
        </div>
    );
}
