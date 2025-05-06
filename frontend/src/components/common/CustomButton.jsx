import React, { useState } from 'react'
import { Button } from '../ui/button'
import { cn } from '@/lib/utils'
import { ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

const CustomButton = ({
    variant = 'default',
    children,
    className,
    ...props
}) => {
    const [isHovered, setIsHovered] = useState(false)

    const buttonStyles = {
        default: 'bg-black text-white hover:bg-black/80',
        outline: 'bg-white text-black border border-gray-200 hover:bg-gray-50',
    }

    return (
      <Button
        className={cn(
          "rounded-none w-full py-6 px-4 font-medium text-base uppercase tracking-wide relative group",
          buttonStyles[variant],
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        {...props}
      >
        <div className="flex items-center justify-center gap-2">
          <motion.span
            animate={{
              x: isHovered ? -3 : 0,
              transition: {
                duration: 0.3,
                ease: "easeOut"
              }
            }}
          >
            {children}
          </motion.span>
          <motion.div
            initial={{ opacity: 0, x: -10, scale: 0.8, rotate: -10 }}
            animate={{
              opacity: isHovered ? 1 : 0,
              x: isHovered ? 0 : -10,
              scale: isHovered ? 1 : 0.8,
              rotate: isHovered ? 0 : -10,
              transition: {
                duration: 0.3,
                ease: [0.19, 1.0, 0.22, 1.0], // Cubic bezier for a more elegant motion
                scale: {
                  duration: 0.2,
                  ease: "backOut"
                },
                rotate: {
                  duration: 0.2,
                  ease: "backOut"
                }
              }
            }}
            className="origin-center"
          >
            <ArrowRight size={18} className="stroke-current" />
          </motion.div>
        </div>
      </Button>
    )
}

export default CustomButton