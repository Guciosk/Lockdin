'use client';

import { Button } from "@/components/ui/button";
import { useFormStatus } from "react-dom";

interface SubmitButtonProps {
  children: React.ReactNode;
  formAction?: (prevState: any, formData: FormData) => Promise<any>;
  pendingText?: string;
}

export function SubmitButton({ children, pendingText = "Loading..." }: SubmitButtonProps) {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" disabled={pending}>
      {pending ? pendingText : children}
    </Button>
  );
} 