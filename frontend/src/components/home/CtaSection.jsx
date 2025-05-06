import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const CtaSection = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.3 });

  return (
    <section className="py-20 bg-primary text-primary-foreground" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">
            Stop overpaying for products online
          </h2>
          <p className="text-lg font-serif mb-8 max-w-2xl mx-auto opacity-90">
            Join thousands of smart Kenyan shoppers using Thamani
          </p>
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <a
              href="/signup"
              className="inline-block px-8 py-4 bg-white dark:bg-black text-black dark:text-white font-serif font-bold text-lg border border-white hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
            >
              Sign Up — It's Free
            </a>
          </motion.div>
          <p className="mt-4 text-sm opacity-80">
            No credit card required • Free price alerts • Cancel anytime
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default CtaSection;
