import { cn } from "@/lib/utils";

export type Message = {
  type: "error" | "success";
  message: string;
};

interface FormMessageProps {
  message?: Message;
  className?: string;
}

export function FormMessage({ message, className }: FormMessageProps) {
  if (!message) return null;

  return (
    <div
      className={cn(
        "mt-2 text-sm",
        message.type === "error" ? "text-red-500" : "text-green-500",
        className
      )}
    >
      {message.message}
    </div>
  );
} 