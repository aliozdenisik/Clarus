"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useRef, useState, MouseEvent } from "react"
import { cn } from "@/lib/utils"

interface MagneticButtonProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  disabled?: boolean
  type?: "button" | "submit" | "reset"
}

export function MagneticButton({
  children,
  className,
  onClick,
  disabled,
  type = "button",
}: MagneticButtonProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const rectRef = useRef<DOMRect | null>(null)

  const handleMouseEnter = (e: MouseEvent<HTMLButtonElement>) => {
    rectRef.current = e.currentTarget.getBoundingClientRect()
  }

  const handleMouseMove = (e: MouseEvent<HTMLButtonElement>) => {
    const rect = rectRef.current ?? e.currentTarget.getBoundingClientRect()
    if (!rectRef.current) {
      rectRef.current = rect
    }

    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const deltaX = (e.clientX - centerX) * 0.15
    const deltaY = (e.clientY - centerY) * 0.15
    setPosition({ x: deltaX, y: deltaY })
  }

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 })
    rectRef.current = null
  }

  return (
    <motion.button
      className={cn(
        "relative rounded-md bg-[var(--color-accent-primary)] px-4 py-2 text-sm font-medium text-white",
        className
      )}
      style={{ x: position.x, y: position.y }}
      transition={springPresets.snappy}
      onMouseEnter={handleMouseEnter}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
      type={type}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  )
}
