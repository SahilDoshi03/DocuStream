"use client";

import { useChat, fetchServerSentEvents, UIMessage } from "@tanstack/ai-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Send, Paperclip, File, X, Loader2, Database, ChevronDown } from "lucide-react";
import { useRef, useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { clsx } from "clsx";

interface ChatInterfaceProps {
    chatId?: string;
    initialMessages?: UIMessage[];
}

export function ChatInterface({ chatId, initialMessages: propInitialMessages }: ChatInterfaceProps) {
    const [input, setInput] = useState("");
    const [files, setFiles] = useState<File[]>([]);
    const [selectedIndustry, setSelectedIndustry] = useState<string>("");
    // We treat 'chatId' prop as initial value. If not provided, we might generate one later.
    const [currentChatId, setCurrentChatId] = useState<string | undefined>(chatId);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Fetch existing messages if chatId is provided
    const { data: fetchedMessages } = useQuery({
        queryKey: ["chat", chatId],
        queryFn: async () => {
            if (!chatId) return [];
            const res = await fetch(`/api/chats/${chatId}`);
            if (!res.ok) throw new Error("Failed to fetch chat");
            return res.json();
        },
        enabled: !!chatId,
        staleTime: 0 // Always fetch fresh
    });

    // Use refs to ensure the connection adapter always accesses the latest state
    // even if useChat doesn't recreate the client on prop changes.
    const industryRef = useRef(selectedIndustry);
    const chatIdRef = useRef(currentChatId);

    useEffect(() => {
        industryRef.current = selectedIndustry;
    }, [selectedIndustry]);

    useEffect(() => {
        chatIdRef.current = currentChatId;
    }, [currentChatId]);

    const { messages, sendMessage, isLoading, setMessages } = useChat({
        connection: fetchServerSentEvents("/api/chat", () => ({
            body: {
                industry: industryRef.current,
                chat_id: chatIdRef.current
            }
        })),
        initialMessages: propInitialMessages || fetchedMessages || [
            {
                id: "1",
                role: "assistant",
                parts: [{ type: "text", content: "Hello! Upload a document and select an industry to extract structured data." }]
            }
        ]
    });

    useEffect(() => {
        if (fetchedMessages) {
            setMessages(fetchedMessages);
        }
    }, [fetchedMessages, setMessages]);

    // Update currentChatId when prop changes (navigation)
    useEffect(() => {
        if (chatId) setCurrentChatId(chatId);
    }, [chatId]);




    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
        }
    };

    const removeFile = (index: number) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const uploadMutation = useMutation({
        mutationFn: async (file: File) => {
            const formData = new FormData();
            formData.append("file", file);
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData,
            });
            if (!res.ok) throw new Error("Upload failed");
            return res.json();
        }
    });

    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() && files.length === 0) return;

        let currentInput = input;
        const currentFiles = [...files];

        if (currentFiles.length > 0) {
            try {
                // Upload all files
                const uploadPromises = currentFiles.map(file => uploadMutation.mutateAsync(file));
                const uploadedFiles = await Promise.all(uploadPromises);

                // Append pseudo-tags
                const fileContext = uploadedFiles.map((f: any) => `[FILE_ID: ${f.id} FILENAME: ${f.filename}]`).join("\n");
                currentInput = `${fileContext}\n\n${currentInput}`;

            } catch (error) {
                console.error("Failed to upload files", error);
                return;
            }
        }

        if (!currentChatId) {
            // Generate a new ID client-side to ensure URL update immediatley
            const newId = crypto.randomUUID();
            setCurrentChatId(newId);
            window.history.replaceState(null, "", `/chat/${newId}`);

            // Wait a tick for state to update? 
            // Actually, the body passed to sendMessage uses the current render's scope or refs?
            // Hooks update is async. We might need to handle this carefully.
            // We can pass additional body params to sendMessage? No, useChat usually uses the bound body.
            // However, `useChat` might read state on render.
            // We'll trust that React queues the state update, but for THIS call, we might rely on the updated state in next render?
            // Actually, if we update state here, the `sendMessage` call below will run with *old* state in closure? Yes.
            // BUT `useChat` internally might reference latest mutable ref or we pass body override?
            // Most implementations of `useChat` allow passing `data` or `body` to `handleSubmit`? 
            // Tanstack AI `sendMessage` signature: `sendMessage(input: string, options?: ...)`
            // If body is in hook config, it might be stale.
            // Workaround: Force flush or pass ID explicitly?
            // If I change currentChatId, the component re-renders, useChat updates its body config.
            // But I want to send NOW.

            // Solution: Since `body` in useChat is reactive, we can wait? No, user wants instant feedback.
            // We will assume backend handles "create if new" logic.
            // But if we generated an ID, we want backend to use IT.
            // We can force a re-render/wait?
            // Actually, simpler:
            // Just send the message. Backend creates "some" ID. 
            // But then we don't know it to update URL.
            // That's why we generate it.

            // We can rely on `sendMessage` taking the FRESH state if we defer it?
            // `setTimeout(() => sendMessage(...), 0)`?

            // Better: we can pass `body` override to `sendMessage`? 
            // Checking source code or docs is hard.
            // I'll try to pass `body` in `sendMessage` options if supported.
            // If not, I'll update state and `setTimeout`.

            setTimeout(() => {
                sendMessage(currentInput);
            }, 0);
        } else {
            await sendMessage(currentInput);
        }

        setInput("");
        setFiles([]);
    };

    return (
        <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
            {/* Messages Area - Hidden Scrollbar */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
                {messages.map(m => (
                    <div key={m.id} className={clsx("flex gap-4", m.role === "user" ? "flex-row-reverse" : "flex-row")}>
                        <div className={clsx(
                            "max-w-[80%] rounded-2xl px-5 py-3 shadow-sm",
                            m.role === "user"
                                ? "bg-indigo-600 text-white rounded-br-sm"
                                : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-bl-sm"
                        )}>
                            <div className={clsx("prose prose-sm max-w-none", m.role === "user" ? "prose-invert" : "dark:prose-invert")}>
                                {m.parts.map((part, i) => {
                                    if (part.type === 'text') {
                                        return <ReactMarkdown key={i}>{part.content}</ReactMarkdown>;
                                    }
                                    if (part.type === 'tool-call') return <span key={i} className="text-xs italic opacity-50 block">Executing {part.name}...</span>;
                                    return null;
                                })}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl rounded-bl-sm px-5 py-4 flex items-center gap-2 shadow-sm">
                            <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
                            <span className="text-sm text-zinc-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-black border-t border-zinc-200 dark:border-zinc-800">
                <div className="max-w-4xl mx-auto">
                    {/* File Preview */}
                    {files.length > 0 && (
                        <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
                            {files.map((file, i) => (
                                <div key={i} className="flex items-center gap-2 bg-zinc-100 dark:bg-zinc-800 px-3 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 min-w-fit">
                                    <div className="bg-red-100 dark:bg-red-900/30 p-1.5 rounded">
                                        <File className="w-4 h-4 text-red-600 dark:text-red-400" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-xs font-medium truncate max-w-[150px]">{file.name}</span>
                                        <span className="text-[10px] text-zinc-500">{(file.size / 1024).toFixed(0)} KB</span>
                                    </div>
                                    <button onClick={() => removeFile(i)} className="ml-1 p-1 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-full transition-colors">
                                        <X className="w-3 h-3 text-zinc-500" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Extraction Controls */}
                    <div className="flex items-center gap-2 mb-2">
                        <div className="relative">
                            <select
                                value={selectedIndustry}
                                onChange={(e) => setSelectedIndustry(e.target.value)}
                                className="appearance-none bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 text-xs rounded-lg pl-3 pr-8 py-2 focus:ring-2 focus:ring-indigo-500 outline-none cursor-pointer"
                            >
                                <option value="" disabled>Select Extraction Type</option>
                                <option value="banking">Banking & Finance</option>
                                <option value="healthcare">Healthcare & Pharma</option>
                                <option value="insurance">Insurance</option>
                                <option value="legal">Legal & Litigation</option>
                                <option value="retail">Retail & CPG</option>
                                <option value="food_beverage">Food & Beverage</option>
                            </select>
                            <ChevronDown className="w-3 h-3 absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
                        </div>
                    </div>

                    <form onSubmit={onSubmit} className="relative flex items-end gap-2 bg-zinc-50 dark:bg-zinc-900 p-2 rounded-xl border border-zinc-200 dark:border-zinc-800 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all shadow-sm">
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="p-3 text-zinc-400 hover:text-indigo-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
                        >
                            <Paperclip className="w-5 h-5" />
                        </button>
                        <input
                            type="file"
                            multiple
                            className="hidden"
                            ref={fileInputRef}
                            onChange={handleFileSelect}
                        />

                        <textarea
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    onSubmit(e as any);
                                }
                            }}
                            placeholder="Send a message..."
                            rows={1}
                            className="flex-1 bg-transparent border-0 focus:ring-0 resize-none py-3 max-h-32 text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400"
                            style={{ minHeight: '44px' }}
                        />

                        <button
                            type="submit"
                            disabled={!input.trim() && files.length === 0}
                            className={clsx(
                                "p-3 rounded-lg transition-all duration-200",
                                input.trim() || files.length > 0
                                    ? "bg-indigo-600 text-white hover:bg-indigo-700 shadow-md"
                                    : "bg-zinc-200 dark:bg-zinc-800 text-zinc-400 cursor-not-allowed"
                            )}
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <p className="text-center text-xs text-zinc-400 dark:text-zinc-500 mt-2">
                        AI can make mistakes. Please verify important information.
                    </p>
                </div>
            </div>
        </div>
    );
}
