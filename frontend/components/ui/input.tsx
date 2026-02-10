import { cn } from "@/lib/utils"
import * as React from "react"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "border-input bg-background text-foreground placeholder:text-muted-foreground/70 focus-visible:border-ring focus-visible:ring-ring/20 flex h-9 w-full rounded-lg border px-3 py-2 text-sm shadow-sm shadow-black/5 transition-shadow focus-visible:ring-[3px] focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
          type === "search" &&
            "[&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none [&::-webkit-search-results-button]:appearance-none [&::-webkit-search-results-decoration]:appearance-none",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
