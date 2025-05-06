import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * Loader component with multiple variants
 * @param {Object} props - Component props
 * @param {string} props.variant - Loader variant: 'dots', 'spinner', 'pulse', 'bar', or 'skeleton'
 * @param {string} props.size - Size of the loader: 'sm', 'md', 'lg'
 * @param {string} props.color - Color of the loader: 'primary', 'secondary', 'muted', or any custom class
 * @param {string} props.text - Optional text to display with the loader
 * @param {string} props.className - Additional classes
 * @param {boolean} props.fullScreen - Whether to display the loader full screen with overlay
 */
const Loader = ({
  variant = 'dots',
  size = 'md',
  color = 'primary',
  text,
  className,
  fullScreen = false,
  ...props
}) => {
  // Size mappings
  const sizeMap = {
    sm: {
      dots: 'h-1 w-1',
      spinner: 'h-4 w-4',
      pulse: 'h-4 w-4',
      bar: 'h-0.5',
      text: 'text-xs',
    },
    md: {
      dots: 'h-2 w-2',
      spinner: 'h-8 w-8',
      pulse: 'h-8 w-8',
      bar: 'h-1',
      text: 'text-sm',
    },
    lg: {
      dots: 'h-3 w-3',
      spinner: 'h-12 w-12',
      pulse: 'h-12 w-12',
      bar: 'h-1.5',
      text: 'text-base',
    },
  };

  // Color mappings
  const colorClass = {
    primary: 'bg-primary',
    secondary: 'bg-secondary-foreground',
    muted: 'bg-muted-foreground',
  }[color] || color;

  // Render the appropriate loader based on variant
  const renderLoader = () => {
    switch (variant) {
      case 'dots':
        return (
          <div className="flex space-x-2 justify-center items-center">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className={cn('rounded-full', colorClass, sizeMap[size].dots)}
                initial={{ opacity: 0.4 }}
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  delay: i * 0.2,
                  ease: 'easeInOut',
                }}
              />
            ))}
          </div>
        );

      case 'spinner':
        return (
          <div className="relative">
            <motion.div
              className={cn('rounded-full border-2 border-t-transparent', colorClass, sizeMap[size].spinner)}
              animate={{ rotate: 360 }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: 'linear',
              }}
              style={{ borderTopColor: 'transparent' }}
            />
          </div>
        );

      case 'pulse':
        return (
          <motion.div
            className={cn('rounded-full', colorClass, sizeMap[size].pulse)}
            animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.6, 1, 0.6] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        );

      case 'bar':
        return (
          <div className={cn('w-full overflow-hidden', sizeMap[size].bar)}>
            <motion.div
              className={cn('h-full', colorClass)}
              initial={{ width: '0%' }}
              animate={{ width: ['0%', '100%', '0%'] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </div>
        );

      case 'skeleton':
        return (
          <div className="w-full">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <motion.div
                  className={cn('rounded bg-muted', i === 0 ? 'w-3/4' : 'w-full', sizeMap[size].bar)}
                  initial={{ opacity: 0.4 }}
                  animate={{ opacity: [0.4, 0.7, 0.4] }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  // Full screen loader with overlay
  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm z-50">
        <div className={cn('flex flex-col items-center', className)} {...props}>
          {renderLoader()}
          {text && <p className={cn('mt-4 font-serif text-center', sizeMap[size].text)}>{text}</p>}
        </div>
      </div>
    );
  }

  // Regular inline loader
  return (
    <div className={cn('flex flex-col items-center', className)} {...props}>
      {renderLoader()}
      {text && <p className={cn('mt-2 font-serif text-center', sizeMap[size].text)}>{text}</p>}
    </div>
  );
};

/**
 * Full page loader with overlay
 */
export const FullPageLoader = ({ text = 'Loading...', ...props }) => (
  <Loader fullScreen text={text} variant="dots" size="lg" {...props} />
);

/**
 * Button loader to be used inside buttons
 */
export const ButtonLoader = ({ className, ...props }) => (
  <Loader
    variant="dots"
    size="sm"
    className={cn('inline-flex mr-2', className)}
    {...props}
  />
);

/**
 * Skeleton loader for content placeholders
 */
export const SkeletonLoader = ({ className, ...props }) => (
  <Loader
    variant="skeleton"
    className={cn('w-full', className)}
    {...props}
  />
);

export default Loader;
