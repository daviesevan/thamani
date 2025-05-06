import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { ShoppingBag, ShoppingCart, Store, Package, Truck, Building, Laptop, Smartphone } from 'lucide-react';

const SupportedRetailers = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.3 });

  const retailers = [
    { name: "Jumia Kenya", icon: <ShoppingBag size={32} /> },
    { name: "Kilimall", icon: <ShoppingCart size={32} /> },
    { name: "Masoko", icon: <Store size={32} /> },
    { name: "Jiji Kenya", icon: <Package size={32} /> },
    { name: "Carrefour Kenya", icon: <Truck size={32} /> },
    { name: "Naivas Online", icon: <Building size={32} /> },
    { name: "Electrohub", icon: <Laptop size={32} /> },
    { name: "Avechi", icon: <Smartphone size={32} /> },
  ];

  // Duplicate retailers for seamless marquee effect
  const marqueeRetailers = [...retailers, ...retailers];

  return (
    <section id="supported-shops" className="py-20" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">Supported Retailers</h2>
          <div className="w-20 h-1 bg-primary mx-auto mb-6"></div>
          <p className="text-lg font-serif text-muted-foreground max-w-3xl mx-auto">
            We track thousands of products across Kenya's most popular online retailers
          </p>
        </div>

        <div className="overflow-hidden">
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              className="flex"
              animate={{ x: ["0%", "-50%"] }}
              transition={{
                x: {
                  repeat: Infinity,
                  repeatType: "loop",
                  duration: 30,
                  ease: "linear"
                }
              }}
            >
              {marqueeRetailers.map((retailer, index) => (
                <div 
                  key={index} 
                  className="flex flex-col items-center justify-center mx-8 min-w-[120px]"
                >
                  <div className="w-16 h-16 flex items-center justify-center mb-3 text-primary">
                    {retailer.icon}
                  </div>
                  <span className="font-serif text-sm text-center">{retailer.name}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default SupportedRetailers;
