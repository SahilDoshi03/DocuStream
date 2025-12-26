import { ChatInterface } from "../components/ChatInterface";
import { GoogleDriveConnect } from "../components/GoogleDriveConnect";

export default function Home() {
  return (
    <div className="h-full bg-zinc-50/50 dark:bg-black">
      <div className="absolute top-4 right-4 z-10 w-64">
        <GoogleDriveConnect />
      </div>
      <ChatInterface />
    </div>
  );
}
