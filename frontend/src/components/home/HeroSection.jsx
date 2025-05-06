import React from 'react';
import { Search } from 'lucide-react';
import { motion } from 'framer-motion';

const HeroSection = () => {
  return (
    <section className="pt-32 pb-20 relative overflow-hidden">
      {/* Background typographic elements */}
      <div className="absolute inset-0 overflow-hidden opacity-[0.03] pointer-events-none">
        <div className="absolute -top-10 -left-10 text-[200px] font-serif font-bold">
          Thamani
        </div>
        <div className="absolute bottom-0 right-0 text-[150px] font-serif font-bold">
          Save
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <motion.h1 
            className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold leading-tight mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Track Prices Across Kenya's Top Online Shops
          </motion.h1>
          
          <motion.p 
            className="text-lg md:text-xl font-serif text-muted-foreground mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Get notified when prices drop on Jumia, Kilimall, Masoko and more
          </motion.p>
          
          <motion.div 
            className="max-w-2xl mx-auto mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="relative">
              <input
                type="text"
                placeholder="Paste a product link or search..."
                className="w-full py-4 pl-4 pr-12 border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <button 
                className="absolute right-0 top-0 h-full px-4 flex items-center justify-center bg-primary text-primary-foreground"
                aria-label="Search"
              >
                <Search size={20} />
              </button>
            </div>
          </motion.div>
          
          <motion.div
            className="text-sm font-serif text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <p className="mb-2">Kenyans saved over <span className="font-bold text-foreground">5.3 million KES</span> last month using Thamani</p>
            <div className="flex justify-center space-x-4 text-xs">
              <span>✓ No account required</span>
              <span>✓ Free price alerts</span>
              <span>✓ M-Pesa integration</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
